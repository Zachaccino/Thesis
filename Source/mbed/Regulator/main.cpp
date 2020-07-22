#include "mbed.h"


/* Global variables */
uint32_t Frequency = 0UL;               // Set the default frequency to 0 kHz
double RealDuty[3] = {0.0};             // Set the real duty cycle to 0.0%
double VoltageReference = 5.0 * 1.02;   // Set the reference voltage to 5.0 V
uint32_t u32AdcVoltage = 0;             // Digital value of the voltage
uint32_t u32AdcCurrent = 0;             // Digital value of the current
int32_t ai32ConversionVoltage[3] = {0}; // Save the voltage
int32_t ai32ConversionCurrent[3] = {0}; // Save the current
double VoltageDifference[3] = {0.0};    //	Set the voltage difference


void SYS_Init(void) {
  /* Set PF multi-function pins for XT1_OUT(PF.2) and XT1_IN(PF.3) */
  SYS->GPF_MFPL = (SYS->GPF_MFPL & (~SYS_GPF_MFPL_PF2MFP_Msk)) | XT1_OUT_PF2;
  SYS->GPF_MFPL = (SYS->GPF_MFPL & (~SYS_GPF_MFPL_PF3MFP_Msk)) | XT1_IN_PF3;

  /* Enable HIRC clock (Internal RC 22.1184 MHz) */
  CLK_EnableXtalRC(CLK_PWRCTL_HIRCEN_Msk);

  /* Waiting for HIRC clock ready */
  CLK_WaitClockReady(CLK_STATUS_HIRCSTB_Msk);

  /* Select HCLK clock source as HIRC and and HCLK clock divider as 1 */
  CLK_SetHCLK(CLK_CLKSEL0_HCLKSEL_HIRC, CLK_CLKDIV0_HCLK(1));

  /* Enable HXT clock (external XTAL 12MHz) */
  CLK_EnableXtalRC(CLK_PWRCTL_HXTEN_Msk);

  /* Waiting for HXT clock ready */
  CLK_WaitClockReady(CLK_STATUS_HXTSTB_Msk);

  /* Enable PLL */
  CLK->PLLCTL = CLK_PLLCTL_128MHz_HIRC;

  /* Waiting for PLL stable */
  CLK_WaitClockReady(CLK_STATUS_PLLSTB_Msk);

  /* Select HCLK clock source as PLL and HCLK source divider as 1 (1 for 128
   * MHz, 2 for 64 MHz) */
  CLK_SetHCLK(CLK_CLKSEL0_HCLKSEL_PLL, CLK_CLKDIV0_HCLK(1));

  /* Waiting for PLL clock ready */
  CLK_WaitClockReady(CLK_STATUS_PLLSTB_Msk);

  /* Enable EPWM1 module clock */
  CLK_EnableModuleClock(EPWM1_MODULE);

  CLK_SetModuleClock(EPWM1_MODULE, CLK_CLKSEL2_EPWM1SEL_PCLK1, 0);

  /* Enable UART module clock */
  CLK_EnableModuleClock(UART0_MODULE);

  /* Select UART module clock source as HXT and UART module clock divider as 1
   */
  CLK_SetModuleClock(UART0_MODULE, CLK_CLKSEL1_UART0SEL_HXT,
                     CLK_CLKDIV0_UART0(1));

  /* Reset EPWM1 module */
  SYS_ResetModule(EPWM1_RST);

  /* Update System Core Clock */
  SystemCoreClockUpdate();

  /* Enable EPWM0 module clock */
  CLK_EnableModuleClock(EPWM0_MODULE);

  /* Select EPWM0 module clock source as PCLK0 */
  CLK_SetModuleClock(EPWM0_MODULE, CLK_CLKSEL2_EPWM0SEL_PCLK0, 0);

  /* Enable EADC module clock */
  CLK_EnableModuleClock(EADC_MODULE);

  /* EADC clock source is 64MHz, set divider to 8, EADC clock is 64/8 MHz */
  CLK_SetModuleClock(EADC_MODULE, 0, CLK_CLKDIV0_EADC(8));
  CLK_SetModuleClock(EADC_MODULE, 1, CLK_CLKDIV0_EADC(8));

  /* Set multi-function pins for UART0 RXD and TXD */
  SYS->GPB_MFPH =
      (SYS->GPB_MFPH & (~(UART0_RXD_PB12_Msk | UART0_TXD_PB13_Msk))) |
      UART0_RXD_PB12 | UART0_TXD_PB13;

  /* Set PC multi-function pins for EPWM1 Channel 0~1 */
  SYS->GPC_MFPL = (SYS->GPC_MFPL & (~SYS_GPC_MFPL_PC5MFP_Msk)) | EPWM1_CH0_PC5;
  SYS->GPC_MFPL = (SYS->GPC_MFPL & (~SYS_GPC_MFPL_PC4MFP_Msk)) | EPWM1_CH1_PC4;

  /* Configure the PB2 and PB3 ADC analog input pins.  */
  SYS->GPB_MFPL = (SYS->GPB_MFPL & ~(SYS_GPB_MFPL_PB2MFP_Msk)) | EADC0_CH2_PB2;
  SYS->GPB_MFPL = (SYS->GPB_MFPL & ~(SYS_GPB_MFPL_PB3MFP_Msk)) | EADC0_CH3_PB3;

  /* Disable PB digital input path to avoid the leakage current. */
  GPIO_DISABLE_DIGITAL_PATH(PB, 0xF);

  /* Set PE multi-function pins for EPWM0 Channel0 */
  SYS->GPE_MFPL = (SYS->GPE_MFPL & (~SYS_GPE_MFPL_PE7MFP_Msk)) | EPWM0_CH0_PE7;
}

void UART0_Init() {
  /* Configure UART0 and set UART0 baud rate */
  UART_Open(UART0, 115200);
}

void EPWM0_Init() {
  /* Set EPWM0 timer clock prescaler */
  EPWM_SET_PRESCALER(EPWM0, 0, 0);

  /* Set up counter type */
  EPWM0->CTL1 &= ~EPWM_CTL1_CNTTYPE0_Msk;

  /* Set EPWM0 timer duty */
  EPWM_SET_CMR(EPWM0, 0, 640);

  /* Set EPWM0 timer period (sampling rate is 1e-5s)*/
  EPWM_SET_CNR(EPWM0, 0, 1279);

  /* EPWM period point trigger ADC enable */
  EPWM_EnableADCTrigger(EPWM0, 0, EPWM_TRG_ADC_EVEN_PERIOD);

  /* Set output level at zero, compare up, period(center) and compare down of
   * specified channel */
  EPWM_SET_OUTPUT_LEVEL(EPWM0, BIT0, EPWM_OUTPUT_HIGH, EPWM_OUTPUT_LOW,
                        EPWM_OUTPUT_NOTHING, EPWM_OUTPUT_NOTHING);

  /* Enable output of EPWM0 channel 0 */
  EPWM_EnableOutput(EPWM0, BIT0);
}

void EPWM1_Init() {
  /* Set EPWM1 timer clock prescaler */
  EPWM_SET_PRESCALER(EPWM1, 0, 0);

  /* Set up counter type */
  EPWM1->CTL1 &= ~EPWM_CTL1_CNTTYPE0_Msk;

  /* Set EPWM1 timer duty */
  EPWM_SET_CMR(EPWM1, 0,
               (uint32_t)((SystemCoreClock / Frequency) * RealDuty[0] / 100));

  /* Set EPWM1 timer period */
  EPWM_SET_CNR(EPWM1, 0, SystemCoreClock / Frequency - 1);

  /* Set output level at zero, compare up, period(center) and compare down of
   * specified channel */
  EPWM_SET_OUTPUT_LEVEL(EPWM1, BIT0, EPWM_OUTPUT_HIGH, EPWM_OUTPUT_LOW,
                        EPWM_OUTPUT_NOTHING, EPWM_OUTPUT_NOTHING);
}

void EADC_Function() {
  int32_t ai32ConversionData[2] = {0};
  uint8_t u8Option = 0;

  while (1) {
    ai32ConversionVoltage[2] = ai32ConversionVoltage[1];
    ai32ConversionVoltage[1] = ai32ConversionVoltage[0];

    RealDuty[2] = RealDuty[1];
    RealDuty[1] = RealDuty[0];

    /* Set input mode as single-end and enable the A/D converter */
    EADC_Open(EADC, EADC_CTL_DIFFEN_SINGLE_END);

    /* Configure the sample module 0 for analog input channel 2 and enable EPWM0
     * trigger source */
    EADC_ConfigSampleModule(EADC, 0, EADC_PWM0TG0_TRIGGER, 2);
    /* Configure the sample module 1 for analog input channel 3 and enable EPWM0
     * trigger source */
    EADC_ConfigSampleModule(EADC, 1, EADC_PWM0TG0_TRIGGER, 3);

    /* Clear the A/D ADINT0 interrupt flag for safe */
    EADC_CLR_INT_FLAG(EADC, EADC_STATUS2_ADIF0_Msk);
    /* Clear the A/D ADINT1 interrupt flag for safe */
    EADC_CLR_INT_FLAG(EADC, EADC_STATUS2_ADIF1_Msk);

    /* Enable the sample modules interrupt */
    EADC_ENABLE_INT(EADC, BIT0); // Enable sample module A/D ADINT0 interrupt.
    /* Enable the sample modules interrupt */
    EADC_ENABLE_INT(EADC, BIT1); // Enable sample module A/D ADINT1 interrupt.

    EADC_ENABLE_SAMPLE_MODULE_INT(EADC, 0,
                                  BIT0); // Enable sample module 0 interrupt.
    EADC_ENABLE_SAMPLE_MODULE_INT(EADC, 1,
                                  BIT1); // Enable sample module 1 interrupt.
    NVIC_EnableIRQ(EADC0_IRQn);
    NVIC_EnableIRQ(EADC1_IRQn);

    /* Reset the EADC indicator and enable EPWM0 channel 0 counter */
    u32AdcVoltage = 0;
    u32AdcCurrent = 0;
    EPWM_Start(EPWM0, BIT0); // EPWM0 channel 0 counter start running.

    /* Wait ADC interrupt (u32AdcVoltage and u32AdcCurrent will be set at
     * IRQ_Handler function) */
    while (u32AdcVoltage == 0 && u32AdcCurrent == 0)
      ;

    /* Reset the ADC interrupt indicator */
    u32AdcVoltage = 0;
    u32AdcCurrent = 0;

    /* Get the conversion result of the sample modules 0 and 1 */
    ai32ConversionData[0] = EADC_GET_CONV_DATA(EADC, 0);
    ai32ConversionData[1] = EADC_GET_CONV_DATA(EADC, 1);

    /* Disable EPWM0 channel 0 counter */
    EPWM_ForceStop(EPWM0, BIT0); // EPWM0 counter stop running.

    /* Disable sample modules interrupt */
    EADC_DISABLE_SAMPLE_MODULE_INT(EADC, 0, BIT0);
    // EADC_DISABLE_SAMPLE_MODULE_INT(EADC, 1, BIT1);

    ai32ConversionVoltage[0] = ai32ConversionData[0];
    // ai32ConversionCurrent[0] = ai32ConversionData[1];

    VoltageDifference[0] =
        VoltageReference - 2 * ((double)ai32ConversionVoltage[0] / 4096) * 3.3;
    VoltageDifference[1] =
        VoltageReference - 2 * ((double)ai32ConversionVoltage[1] / 4096) * 3.3;
    VoltageDifference[2] =
        VoltageReference - 2 * ((double)ai32ConversionVoltage[2] / 4096) * 3.3;

    RealDuty[0] = 0.6333 * RealDuty[1] + 0.3667 * RealDuty[2] +
                  0.2045 * VoltageDifference[0] -
                  0.3081 * VoltageDifference[1] + 0.154 * VoltageDifference[2];

    printf("V_n =    %lf, V_n-1 =    %lf,    V_n-2 =    %lf\n",
           2 * ((double)ai32ConversionVoltage[0] / 4096) * 3.3,
           2 * ((double)ai32ConversionVoltage[1] / 4096) * 3.3,
           2 * ((double)ai32ConversionVoltage[2] / 4096) * 3.3);

    /* Set EPWM1 timer duty */
    EPWM_SET_CMR(EPWM1, 0,
                 (uint32_t)((SystemCoreClock / Frequency) * RealDuty[0] / 100));
  }
}

void EADC0_IRQHandler(void) {
  EADC_CLR_INT_FLAG(
      EADC, EADC_STATUS2_ADIF0_Msk); /* Clear the A/D ADINT0 interrupt flag */
  u32AdcVoltage = 1;
}

void EADC1_IRQHandler(void) {
  EADC_CLR_INT_FLAG(
      EADC, EADC_STATUS2_ADIF1_Msk); /* Clear the A/D ADINT0 interrupt flag */
  u32AdcCurrent = 1;
}

int main(void) {

  uint8_t u8Option = 0;

  /* Unlock protected registers */
  SYS_UnlockReg();

  /* Init System, IP clock and multi-function I/O */
  SYS_Init();

  /* Lock protected registers */
  SYS_LockReg();

  /* Init UART to 115200-8n1 for print message */
  UART0_Init();

  /* Set PWM Frequency and Duty */
  printf("Give PWM Frequency Setting (Hz) then Press Enter:\n");
  scanf("%d", &Frequency);
  printf("Give PWM On Duty Setting (%%) then Press Enter:\n");
  scanf("%lf", &RealDuty[0]);
  printf("PWM Frequency = %d kHz, On Duty = %lf%%.\n", Frequency / 1000,
         RealDuty[0]);

  /* Print System Data */
  printf("\n\nCPU @ %dHz(PLL@ %dHZ)\n", SystemCoreClock, PllClock);
  printf("+-----------------------------------------------------------+\n");
  printf("|                      EPWM Driver                          |\n");
  printf("|                                                           |\n");
  printf("+-----------------------------------------------------------+\n");
  printf("  This code will output waveforms with EPWM1 channel 0~1.\n");
  printf("  I/O configuration:\n");
  printf("  EPWM1 channel 0: %d kHz, duty %lf%%.\n", Frequency / 1000,
         RealDuty[0]);
  printf("  EPWM1 channel 1: %d kHz, duty %lf%%.\n", Frequency / 1000,
         100 - RealDuty[0]);
  printf("  Waveform output pin: EPWM1_CH0(D3), EPWM1_CH1(D2),\n");

  /* Set EPWM mode as complementary mode */
  EPWM_ENABLE_COMPLEMENTARY_MODE(EPWM1);

  /* Init EPWM1 for Output*/
  EPWM1_Init();

  /* Enable output of EPWM1 channel 0~1 */
  EPWM_EnableOutput(EPWM1, BIT0 | BIT1);

  /* Start EPWM1 counter */
  EPWM_Start(EPWM1, BIT0 | BIT1);

  /* Change Duty */
  while (1) {
    printf("\nOptions: \n");
    printf("[1] Change frequency \n");
    printf("[2] Change on duty \n");
    printf("[3] Change both frequency and on duty \n");
    printf("[4] Voltage Regulation\n");
    printf("[Other] Exit \n");
    u8Option = getchar();

    if (u8Option == '1') {
      /* Change the frequency */
      printf("Give PWM Frequency Setting (Hz) then Press Enter:\n");
      scanf("%d", &Frequency);
    } else if (u8Option == '2') {
      /* Change the on duty */
      printf("Give PWM On Duty Setting (%%) then Press Enter:\n");
      scanf("%lf", &RealDuty[0]);
    } else if (u8Option == '3') {
      /* Change both frequency and on duty */
      printf("Give PWM Frequency Setting (Hz) then Press Enter:\n");
      scanf("%d", &Frequency);
      printf("Give PWM On Duty Setting (%%) then Press Enter:\n");
      scanf("%lf", &RealDuty[0]);
    } else if (u8Option == '4') {
      /* Init EPWM for EADC */
      EPWM0_Init();

      /* EADC function */
      EADC_Function();

      /* Reset EADC module */
      SYS_ResetModule(EADC_RST);

      /* Reset EPWM0 module */
      SYS_ResetModule(EPWM0_RST);

      /* Disable EADC IP clock */
      CLK_DisableModuleClock(EADC_MODULE);

      /* Disable EPWM0 IP clock */
      CLK_DisableModuleClock(EPWM0_MODULE);

      /* Disable External Interrupt */
      NVIC_DisableIRQ(EADC0_IRQn);
      NVIC_DisableIRQ(EADC1_IRQn);
    } else {
      printf("Exit\n");
      break;
    }

    /* Set EPWM1 timer duty */
    EPWM_SET_CMR(EPWM1, 0,
                 (uint32_t)((SystemCoreClock / Frequency) * RealDuty[0] / 100));

    /* Set EPWM1 timer period */
    EPWM_SET_CNR(EPWM1, 0, SystemCoreClock / Frequency - 1);

    /* Print new frequency and on duty */
    printf("  EPWM1 channel 0: %d kHz, duty %lf%%.\n", Frequency / 1000,
           RealDuty[0]);
    printf("  EPWM1 channel 1: %d kHz, duty %lf%%.\n", Frequency / 1000,
           100 - RealDuty[0]);
  }

  /* Stop EPWM1 counter */
  EPWM_ForceStop(EPWM1, BIT0 | BIT1);

  while (1)
    ;
}