#include <avr/io.h>
#include <util/delay.h>

#define LCD_RS PB0
#define LCD_EN PB1

#define GREEN_LED PB2
#define YELLOW_LED PB3
#define RED_LED PB4
#define BUZZER PB5

#define RESET_BUTTON PD2
#define BURNER PD3
#define PUMP PC3

#define BURNER_ON_TEMP 160

#define TEMP_HIGH 180
#define TEMP_TRIP 200

#define PRESSURE_HIGH 12
#define PRESSURE_TRIP 15

#define LEVEL_LOW 40
#define LEVEL_TRIP 20

#define SENSOR_LOW_FAULT 2
#define SENSOR_HIGH_FAULT 1021

unsigned char trip_latched = 0;
unsigned char sensor_fault = 0;


/* =====================================================
   LCD
   ===================================================== */

void lcd_enable(void)
{
    PORTB |= (1 << LCD_EN);
    _delay_us(1);

    PORTB &= ~(1 << LCD_EN);
    _delay_us(100);
}

void lcd_send_nibble(unsigned char data)
{
    PORTD &= 0x0F;
    PORTD |= (data & 0xF0);

    lcd_enable();
}

void lcd_command(unsigned char command)
{
    PORTB &= ~(1 << LCD_RS);

    lcd_send_nibble(command);
    lcd_send_nibble(command << 4);

    _delay_ms(2);
}

void lcd_data(unsigned char data)
{
    PORTB |= (1 << LCD_RS);

    lcd_send_nibble(data);
    lcd_send_nibble(data << 4);

    _delay_ms(1);
}

void lcd_init(void)
{
    DDRB |= (1 << LCD_RS) |
            (1 << LCD_EN) |
            (1 << GREEN_LED) |
            (1 << YELLOW_LED) |
            (1 << RED_LED) |
            (1 << BUZZER);

    DDRD |= 0xF0;

    DDRD &= ~(1 << RESET_BUTTON);
    PORTD |= (1 << RESET_BUTTON);

    DDRD |= (1 << BURNER);

    DDRC |= (1 << PUMP);

    _delay_ms(20);

    PORTB &= ~(1 << LCD_RS);

    lcd_send_nibble(0x30);
    _delay_ms(5);

    lcd_send_nibble(0x30);
    _delay_us(150);

    lcd_send_nibble(0x30);
    _delay_us(150);

    lcd_send_nibble(0x20);

    lcd_command(0x28);
    lcd_command(0x0C);
    lcd_command(0x06);
    lcd_command(0x01);

    _delay_ms(2);
}

void lcd_print(const char *text)
{
    while (*text)
    {
        lcd_data(*text);
        text++;
    }
}

void lcd_print_number(unsigned int number)
{
    char buffer[6];
    unsigned char i = 0;

    if (number == 0)
    {
        lcd_data('0');
        return;
    }

    while (number > 0)
    {
        buffer[i++] = (number % 10) + '0';
        number /= 10;
    }

    while (i > 0)
    {
        lcd_data(buffer[--i]);
    }
}


/* =====================================================
   ADC
   ===================================================== */

void adc_init(void)
{
    ADMUX = (1 << REFS0);

    ADCSRA =
        (1 << ADEN) |
        (1 << ADPS2) |
        (1 << ADPS1) |
        (1 << ADPS0);
}

unsigned int adc_read(unsigned char channel)
{
    ADMUX = (1 << REFS0) | (channel & 0x07);

    _delay_us(100);

    ADCSRA |= (1 << ADSC);

    while (ADCSRA & (1 << ADSC))
    {
    }

    return ADC;
}


/* =====================================================
   UART
   ===================================================== */

void uart_init(void)
{
    unsigned int ubrr = 103;

    UBRR0H = (unsigned char)(ubrr >> 8);
    UBRR0L = (unsigned char)ubrr;

    UCSR0B = (1 << TXEN0);

    UCSR0C =
        (1 << UCSZ01) |
        (1 << UCSZ00);
}

void uart_send_char(char data)
{
    while (!(UCSR0A & (1 << UDRE0)))
    {
    }

    UDR0 = data;
}

void uart_print(const char *text)
{
    while (*text)
    {
        uart_send_char(*text);
        text++;
    }
}

void uart_print_number(unsigned int number)
{
    char buffer[6];
    unsigned char i = 0;

    if (number == 0)
    {
        uart_send_char('0');
        return;
    }

    while (number > 0)
    {
        buffer[i++] = (number % 10) + '0';
        number /= 10;
    }

    while (i > 0)
    {
        uart_send_char(buffer[--i]);
    }
}

void uart_newline(void)
{
    uart_send_char('\r');
    uart_send_char('\n');
}


/* =====================================================
   BUZZER
   WOKWI ACTIVE BUZZER
   ===================================================== */

void buzzer_on(void)
{
    /*
     * Generate approximately 2 kHz tone.
     * This is required for the Wokwi buzzer
     * to actually produce audible sound.
     */

    for (unsigned int i = 0; i < 100; i++)
    {
        PORTB |= (1 << BUZZER);
        _delay_us(250);

        PORTB &= ~(1 << BUZZER);
        _delay_us(250);
    }
}

void buzzer_off(void)
{
    PORTB &= ~(1 << BUZZER);
}


/* =====================================================
   BURNER
   ===================================================== */

void burner_on(void)
{
    PORTD |= (1 << BURNER);
}

void burner_off(void)
{
    PORTD &= ~(1 << BURNER);
}

void automatic_burner_control(unsigned int temperature)
{
    if (temperature < BURNER_ON_TEMP)
    {
        burner_on();
    }
    else
    {
        burner_off();
    }
}


/* =====================================================
   OUTPUT STATES
   ===================================================== */

void normal_output(void)
{
    PORTB |= (1 << GREEN_LED);

    PORTB &= ~(1 << YELLOW_LED);
    PORTB &= ~(1 << RED_LED);

    buzzer_off();
}

void warning_output(void)
{
    PORTB &= ~(1 << GREEN_LED);

    PORTB |= (1 << YELLOW_LED);

    PORTB &= ~(1 << RED_LED);

    buzzer_on();
}

void trip_output(void)
{
    PORTB &= ~(1 << GREEN_LED);
    PORTB &= ~(1 << YELLOW_LED);

    PORTB |= (1 << RED_LED);

    burner_off();

    buzzer_on();
}

void sensor_fault_output(void)
{
    PORTB &= ~(1 << GREEN_LED);
    PORTB &= ~(1 << YELLOW_LED);

    PORTB |= (1 << RED_LED);

    burner_off();

    buzzer_on();
}


/* =====================================================
   PUMP
   ===================================================== */

void pump_on(void)
{
    PORTC |= (1 << PUMP);
}

void pump_off(void)
{
    PORTC &= ~(1 << PUMP);
}


/* =====================================================
   LCD
   ===================================================== */

void display_normal(
    unsigned int temperature,
    unsigned int pressure,
    unsigned int level)
{
    lcd_command(0x80);

    lcd_print("T:");
    lcd_print_number(temperature);
    lcd_print("C P:");
    lcd_print_number(pressure);
    lcd_print("B");

    lcd_command(0xC0);

    lcd_print("L:");
    lcd_print_number(level);
    lcd_print("% NORMAL");
}

void display_warning(
    unsigned int temperature,
    unsigned int pressure,
    unsigned int level)
{
    lcd_command(0x80);

    lcd_print("T:");
    lcd_print_number(temperature);
    lcd_print("C P:");
    lcd_print_number(pressure);
    lcd_print("B");

    lcd_command(0xC0);

    lcd_print("L:");
    lcd_print_number(level);
    lcd_print("% WARNING");
}

void display_emergency(void)
{
    lcd_command(0x80);
    lcd_print("EMERGENCY TRIP ");

    lcd_command(0xC0);
    lcd_print("SYSTEM LOCKED  ");
}

void display_temp_fault(void)
{
    lcd_command(0x80);
    lcd_print("TEMP SENSOR    ");

    lcd_command(0xC0);
    lcd_print("FAULT - LOCKED ");
}

void display_pressure_fault(void)
{
    lcd_command(0x80);
    lcd_print("PRESS SENSOR   ");

    lcd_command(0xC0);
    lcd_print("FAULT - LOCKED ");
}

void display_level_fault(void)
{
    lcd_command(0x80);
    lcd_print("LEVEL SENSOR   ");

    lcd_command(0xC0);
    lcd_print("FAULT - LOCKED ");
}


/* =====================================================
   SERIAL LOGGING
   ===================================================== */

void log_normal(
    unsigned int temperature,
    unsigned int pressure,
    unsigned int level)
{
    uart_print("SYSTEM=NORMAL | T=");
    uart_print_number(temperature);

    uart_print("C | P=");
    uart_print_number(pressure);

    uart_print("B | L=");
    uart_print_number(level);

    uart_print("% | BURNER=");

    if (temperature < BURNER_ON_TEMP)
        uart_print("ON");
    else
        uart_print("OFF");

    uart_print(" | PUMP=");

    if (level < LEVEL_LOW)
        uart_print("ON");
    else
        uart_print("OFF");

    uart_print(" | BUZZER=OFF");

    uart_newline();
}

void log_warning(
    unsigned int temperature,
    unsigned int pressure,
    unsigned int level)
{
    uart_print("SYSTEM=WARNING | T=");
    uart_print_number(temperature);

    uart_print("C | P=");
    uart_print_number(pressure);

    uart_print("B | L=");
    uart_print_number(level);

    uart_print("% | BURNER=");

    if (temperature < BURNER_ON_TEMP)
        uart_print("ON");
    else
        uart_print("OFF");

    uart_print(" | PUMP=");

    if (level < LEVEL_LOW)
        uart_print("ON");
    else
        uart_print("OFF");

    uart_print(" | BUZZER=ON");

    uart_newline();
}

void log_emergency(
    unsigned int temperature,
    unsigned int pressure,
    unsigned int level)
{
    uart_print("SYSTEM=EMERGENCY | T=");
    uart_print_number(temperature);

    uart_print("C | P=");
    uart_print_number(pressure);

    uart_print("B | L=");
    uart_print_number(level);

    uart_print("% | BURNER=OFF | PUMP=");

    if (level < LEVEL_LOW)
        uart_print("ON");
    else
        uart_print("OFF");

    uart_print(" | BUZZER=ON");

    uart_newline();
}

void log_sensor_fault(unsigned char fault)
{
    uart_print("SENSOR_FAULT | ");

    if (fault == 1)
        uart_print("TEMPERATURE");
    else if (fault == 2)
        uart_print("PRESSURE");
    else
        uart_print("LEVEL");

    uart_print(" | BURNER=OFF | ALARM=ON");

    uart_newline();
}


/* =====================================================
   MAIN
   ===================================================== */

int main(void)
{
    unsigned int temperature_adc;
    unsigned int pressure_adc;
    unsigned int level_adc;

    unsigned int temperature;
    unsigned int pressure;
    unsigned int level;

    lcd_init();
    adc_init();
    uart_init();

    burner_off();
    pump_off();

    uart_print("================================");
    uart_newline();

    uart_print("INDUSTRIAL BOILER MONITORING");
    uart_newline();

    uart_print("AUTOMATIC CONTROL + SAFETY");
    uart_newline();

    uart_print("SYSTEM STARTED");
    uart_newline();

    uart_print("================================");
    uart_newline();

    while (1)
    {
        /* Read sensors */

        temperature_adc = adc_read(0);
        pressure_adc = adc_read(1);
        level_adc = adc_read(2);

        /* Sensor fault */

        sensor_fault = 0;

        if (temperature_adc <= SENSOR_LOW_FAULT ||
            temperature_adc >= SENSOR_HIGH_FAULT)
        {
            sensor_fault = 1;
        }

        if (pressure_adc <= SENSOR_LOW_FAULT ||
            pressure_adc >= SENSOR_HIGH_FAULT)
        {
            sensor_fault = 2;
        }

        if (level_adc <= SENSOR_LOW_FAULT ||
            level_adc >= SENSOR_HIGH_FAULT)
        {
            sensor_fault = 3;
        }

        /* Convert */

        temperature =
            (temperature_adc * 250UL) / 1023UL;

        pressure =
            (pressure_adc * 20UL) / 1023UL;

        level =
            (level_adc * 100UL) / 1023UL;

        /* Sensor fault */

        if (sensor_fault != 0)
        {
            sensor_fault_output();

            pump_off();

            if (sensor_fault == 1)
                display_temp_fault();
            else if (sensor_fault == 2)
                display_pressure_fault();
            else
                display_level_fault();

            log_sensor_fault(sensor_fault);

            _delay_ms(500);

            continue;
        }

        /* Emergency latch */

        if (temperature >= TEMP_TRIP ||
            pressure >= PRESSURE_TRIP ||
            level < LEVEL_TRIP)
        {
            trip_latched = 1;
        }

        /*
         * RESET
         *
         * Boiler can return to normal only when:
         *
         * Temperature < 180 C
         * Pressure < 12 bar
         * Level >= 40%
         */

        if (!(PIND & (1 << RESET_BUTTON)))
        {
            if (temperature < TEMP_HIGH &&
                pressure < PRESSURE_HIGH &&
                level >= LEVEL_LOW)
            {
                trip_latched = 0;

                uart_print("SYSTEM RESET -> NORMAL");
                uart_newline();
            }

            _delay_ms(300);
        }

        /* Pump */

        if (level < LEVEL_LOW)
            pump_on();
        else
            pump_off();

        /* EMERGENCY */

        if (trip_latched)
        {
            trip_output();

            if (level < LEVEL_LOW)
                pump_on();
            else
                pump_off();

            display_emergency();

            log_emergency(
                temperature,
                pressure,
                level);
        }

        /* WARNING */

        else if (temperature >= TEMP_HIGH ||
                 pressure >= PRESSURE_HIGH ||
                 level < LEVEL_LOW)
        {
            warning_output();

            automatic_burner_control(temperature);

            display_warning(
                temperature,
                pressure,
                level);

            log_warning(
                temperature,
                pressure,
                level);
        }

        /* NORMAL */

        else
        {
            normal_output();

            automatic_burner_control(temperature);

            display_normal(
                temperature,
                pressure,
                level);

            log_normal(
                temperature,
                pressure,
                level);
        }

        _delay_ms(500);
    }

    return 0;
}
