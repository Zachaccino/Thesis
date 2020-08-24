#include "regulator.h"
#include "NuMicro.h"

Regulator::Regulator()
    : AdcVoltageIn(AnalogIn(A0)), 
      AdcCurrentIn(AnalogIn(A1)), 
      AdcVoltageOut(AnalogIn(A2)), 
      AdcCurrentOut(AnalogIn(A3)), 
      Frequency(0UL), 
      VoltageReference(5.0) {}

void Regulator::sys_init() {
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

    /* Set multi-function pins for UART0 RXD and TXD */
    SYS->GPB_MFPH =
        (SYS->GPB_MFPH & (~(UART0_RXD_PB12_Msk | UART0_TXD_PB13_Msk))) |
        UART0_RXD_PB12 | UART0_TXD_PB13;

    /* Set PC multi-function pins for EPWM1 Channel 0~1 */
    SYS->GPC_MFPL = (SYS->GPC_MFPL & (~SYS_GPC_MFPL_PC5MFP_Msk)) | EPWM1_CH0_PC5;
    SYS->GPC_MFPL = (SYS->GPC_MFPL & (~SYS_GPC_MFPL_PC4MFP_Msk)) | EPWM1_CH1_PC4;
}

void Regulator::uart_init() {
    /* Configure UART0 and set UART0 baud rate */
    UART_Open(UART0, 115200);
}

void Regulator::epwm_init() {
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

void Regulator::regulate_voltage() {
    while (true) {
        DigitalVoltageOut[2] = DigitalVoltageOut[1];
        DigitalVoltageOut[1] = DigitalVoltageOut[0];
        
        RealDuty[2] = RealDuty[1];
        RealDuty[1] = RealDuty[0];
        
        /* Read data */
        DigitalVoltageIn = AdcVoltageIn.read()*3.3f;
        DigitalCurrentIn = AdcCurrentIn.read()*3.3f;
        DigitalVoltageOut[0] = AdcVoltageOut.read()*3.3f;
        DigitalCurrentOut = AdcCurrentOut.read()*3.3f;
        
        VoltageDifference[0] = VoltageReference - 3*DigitalVoltageOut[0];
        VoltageDifference[1] = VoltageReference - 3*DigitalVoltageOut[1];
        VoltageDifference[2] = VoltageReference - 3*DigitalVoltageOut[2];
        
        /* voltage regulation equation */
        RealDuty[0] = 0.6333 * RealDuty[1] + 
                        0.3667 * RealDuty[2] + 
                        0.2045 * VoltageDifference[0] - 
                        0.3081 * VoltageDifference[1] + 
                        0.1540 * VoltageDifference[2];
        
        /* Set EPWM1 timer duty */
        EPWM_SET_CMR(EPWM1, 0, 
                    (uint32_t)((SystemCoreClock/Frequency)*RealDuty[0]/100));
        
        /* ADC sampling rate is 1/100us=10kHz */
        wait_us(100);
    }
}

void Regulator::change_frequency(uint32_t target) {
    Frequency = target;
}

void Regulator::change_duty(double target) {
    RealDuty[0] = target;
}

void Regulator::commit_changes() {
    /* Set EPWM1 timer duty */
    EPWM_SET_CMR(EPWM1, 0,
                 (uint32_t)((SystemCoreClock / Frequency) * RealDuty[0] / 100));

    /* Set EPWM1 timer period */
    EPWM_SET_CNR(EPWM1, 0, SystemCoreClock / Frequency - 1);
}

void Regulator::stage_one_init() {
    /* Unlock protected registers */
    SYS_UnlockReg();

    /* Init System, IP clock and multi-function I/O */
    sys_init();

    /* Lock protected registers */
    SYS_LockReg();

    /* Init UART to 115200-8n1 for print message */
    uart_init();
}

void Regulator::stage_two_init() {
    /* Set EPWM mode as complementary mode */
    EPWM_ENABLE_COMPLEMENTARY_MODE(EPWM1);

    /* Init EPWM1 for Output*/
    epwm_init();

    /* Enable output of EPWM1 channel 0~1 */
    EPWM_EnableOutput(EPWM1, BIT0 | BIT1);

    /* Start EPWM1 counter */
    EPWM_Start(EPWM1, BIT0 | BIT1);
}

uint32_t Regulator::get_frequency() {
    return Frequency;
}

double Regulator::get_duty() {
    return RealDuty[0];
}


Regulator::~Regulator() {
    /* Stop EPWM1 counter */
    EPWM_ForceStop(EPWM1, BIT0 | BIT1);
}

double Regulator::voltage_in() {
    return 3 * DigitalVoltageIn;
}

double Regulator::current_in() {
    return 3 * DigitalCurrentIn;
}

double Regulator::voltage_out() {
    return 3 * DigitalVoltageOut[0];
}

double Regulator::current_out() {
    return 3 * DigitalCurrentOut;
}