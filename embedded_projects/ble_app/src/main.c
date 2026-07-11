#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/sys/printk.h>

/* --- 1. HARDWARE MAPPING --- */
#define LED0_NODE DT_ALIAS(led0)
static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(LED0_NODE, gpios);

#define STACKSIZE 1024
#define PRIORITY 7

/* --- 2. THE SEMAPHORES (The Tokens) --- */
K_SEM_DEFINE(thread_a_sem, 1, 1); /* Thread A gets the green light first */
K_SEM_DEFINE(thread_b_sem, 0, 1); /* Thread B is locked at boot */


/* --- 3. THE SHARED ENGINE --- 
 * Both threads run this exact same function, but pass different parameters.
 */
void led_ping_pong_engine(const char *name, struct k_sem *my_sem, struct k_sem *other_sem, int led_target_state)
{
	while (1) {
		/* 1. Wait for my turn */
		k_sem_take(my_sem, K_FOREVER);

		/* 2. Change the physical LED state */
		gpio_pin_set_dt(&led, led_target_state);

		/* 3. Print to the USB Console */
		printk("%s set the LED %s!\n", name, led_target_state ? "ON" : "OFF");

		/* 4. Keep the LED in this state for 500ms */
		k_msleep(500);

		/* 5. Wake up the OTHER thread */
		k_sem_give(other_sem);
	}
}


/* --- 4. THREAD B: THE STATIC ROUTE --- 
 * Created at compile time. It runs automatically in the background.
 */
void thread_b_entry(void *dummy1, void *dummy2, void *dummy3)
{
	/* Thread B's job is to turn the LED OFF (0) */
	led_ping_pong_engine("Thread B [STATIC]", &thread_b_sem, &thread_a_sem, 0);
}
/* This macro builds and launches Thread B automatically */
K_THREAD_DEFINE(thread_b_id, STACKSIZE, thread_b_entry, NULL, NULL, NULL, PRIORITY, 0, 0);


/* --- 5. THREAD A: THE DYNAMIC ROUTE --- 
 * We manually allocate the RAM here, but we don't start it yet.
 */
void thread_a_entry(void *dummy1, void *dummy2, void *dummy3)
{
	/* Thread A's job is to turn the LED ON (1) */
	led_ping_pong_engine("Thread A [DYNAMIC]", &thread_a_sem, &thread_b_sem, 1);
}
/* Manually define the stack array and the Thread Control Block (TCB) */
K_THREAD_STACK_DEFINE(thread_a_stack, STACKSIZE);
static struct k_thread thread_a_data;


/* --- 6. THE MAIN GATEKEEPER --- */
int main(void)
{
	/* A. Wait for the USB Serial to connect */
	const struct device *const dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));
	uint32_t dtr = 0;
	if (device_is_ready(dev)) {
		while (!dtr) {
			uart_line_ctrl_get(dev, UART_LINE_CTRL_DTR, &dtr);
			k_sleep(K_MSEC(100));
		}
	}

	/* B. Initialize the Physical LED Hardware */
	if (!gpio_is_ready_dt(&led)) {
		printk("Error: LED device is not ready\n");
		return 0;
	}
	gpio_pin_configure_dt(&led, GPIO_OUTPUT_ACTIVE);

	printk("\n--- Starting Hybrid Thread Demo ---\n");

	/* C. Dynamically Create Thread A (Frozen) */
	k_thread_create(&thread_a_data, thread_a_stack,
			K_THREAD_STACK_SIZEOF(thread_a_stack),
			thread_a_entry, NULL, NULL, NULL,
			PRIORITY, 0, K_FOREVER);

	/* D. SMP Core Pinning (Optional, if CONFIG_SMP=y is in prj.conf) */
/* D. SMP Core Pinning (Protected by Preprocessor!) */
#if IS_ENABLED(CONFIG_SMP) && IS_ENABLED(CONFIG_SCHED_CPU_MASK)
	if (arch_num_cpus() > 1) {
		k_thread_cpu_pin(&thread_a_data, 0);
		
		k_thread_suspend(thread_b_id);
		k_thread_cpu_pin(thread_b_id, 1);
		k_thread_resume(thread_b_id);
	}
#endif
	/* E. Pull the trigger to start Thread A! */
	k_thread_start(&thread_a_data);

	/* main() is done. The RTOS scheduler takes over completely. */
	return 0;
}
