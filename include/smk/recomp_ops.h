/*
 * Width-accurate arithmetic helpers used by generated SMK functions.
 *
 * These mirror the 65C816 binary/BCD ADC and SBC behavior used by the
 * LakeSnes oracle while operating on snesrecomp's public g_cpu state.
 */
#ifndef SMK_RECOMP_OPS_H
#define SMK_RECOMP_OPS_H

#include <snesrecomp/snesrecomp.h>
#include <stdint.h>

static inline void smk_op_adc8(uint8_t value) {
    uint16_t a = (uint8_t)g_cpu.C;
    int result;
    if (g_cpu.flag_D) {
        result = (a & 0x0F) + (value & 0x0F) + (g_cpu.flag_C ? 1 : 0);
        if (result > 0x09) result = ((result + 0x06) & 0x0F) + 0x10;
        result = (a & 0xF0) + (value & 0xF0) + result;
    } else {
        result = a + value + (g_cpu.flag_C ? 1 : 0);
    }
    g_cpu.flag_V = ((a & 0x80) == (value & 0x80)) &&
                   ((value & 0x80) != (result & 0x80));
    if (g_cpu.flag_D && result > 0x9F) result += 0x60;
    g_cpu.flag_C = result > 0xFF;
    g_cpu.C = (uint16_t)((g_cpu.C & 0xFF00) | (result & 0xFF));
    cpu_update_nz8((uint8_t)g_cpu.C);
}

static inline void smk_op_adc16(uint16_t value) {
    uint16_t a = g_cpu.C;
    int result;
    if (g_cpu.flag_D) {
        result = (a & 0x000F) + (value & 0x000F) + (g_cpu.flag_C ? 1 : 0);
        if (result > 0x0009) result = ((result + 0x0006) & 0x000F) + 0x0010;
        result = (a & 0x00F0) + (value & 0x00F0) + result;
        if (result > 0x009F) result = ((result + 0x0060) & 0x00FF) + 0x0100;
        result = (a & 0x0F00) + (value & 0x0F00) + result;
        if (result > 0x09FF) result = ((result + 0x0600) & 0x0FFF) + 0x1000;
        result = (a & 0xF000) + (value & 0xF000) + result;
    } else {
        result = a + value + (g_cpu.flag_C ? 1 : 0);
    }
    g_cpu.flag_V = ((a & 0x8000) == (value & 0x8000)) &&
                   ((value & 0x8000) != (result & 0x8000));
    if (g_cpu.flag_D && result > 0x9FFF) result += 0x6000;
    g_cpu.flag_C = result > 0xFFFF;
    g_cpu.C = (uint16_t)result;
    cpu_update_nz16(g_cpu.C);
}

static inline void smk_op_sbc8(uint8_t operand) {
    uint16_t a = (uint8_t)g_cpu.C;
    uint8_t value = (uint8_t)(operand ^ 0xFF);
    int result;
    if (g_cpu.flag_D) {
        result = (a & 0x0F) + (value & 0x0F) + (g_cpu.flag_C ? 1 : 0);
        if (result < 0x10) {
            int adjusted = result - 0x06;
            result = adjusted & (adjusted < 0 ? 0x0F : 0x1F);
        }
        result = (a & 0xF0) + (value & 0xF0) + result;
    } else {
        result = a + value + (g_cpu.flag_C ? 1 : 0);
    }
    g_cpu.flag_V = ((a & 0x80) == (value & 0x80)) &&
                   ((value & 0x80) != (result & 0x80));
    if (g_cpu.flag_D && result < 0x100) result -= 0x60;
    g_cpu.flag_C = result > 0xFF;
    g_cpu.C = (uint16_t)((g_cpu.C & 0xFF00) | (result & 0xFF));
    cpu_update_nz8((uint8_t)g_cpu.C);
}

static inline void smk_op_sbc16(uint16_t operand) {
    uint16_t a = g_cpu.C;
    uint16_t value = (uint16_t)(operand ^ 0xFFFF);
    int result;
    if (g_cpu.flag_D) {
        result = (a & 0x000F) + (value & 0x000F) + (g_cpu.flag_C ? 1 : 0);
        if (result < 0x0010) {
            int adjusted = result - 0x0006;
            result = adjusted & (adjusted < 0 ? 0x000F : 0x001F);
        }
        result = (a & 0x00F0) + (value & 0x00F0) + result;
        if (result < 0x0100) {
            int adjusted = result - 0x0060;
            result = adjusted & (adjusted < 0 ? 0x00FF : 0x01FF);
        }
        result = (a & 0x0F00) + (value & 0x0F00) + result;
        if (result < 0x1000) {
            int adjusted = result - 0x0600;
            result = adjusted & (adjusted < 0 ? 0x0FFF : 0x1FFF);
        }
        result = (a & 0xF000) + (value & 0xF000) + result;
    } else {
        result = a + value + (g_cpu.flag_C ? 1 : 0);
    }
    g_cpu.flag_V = ((a & 0x8000) == (value & 0x8000)) &&
                   ((value & 0x8000) != (result & 0x8000));
    if (g_cpu.flag_D && result < 0x10000) result -= 0x6000;
    g_cpu.flag_C = result > 0xFFFF;
    g_cpu.C = (uint16_t)result;
    cpu_update_nz16(g_cpu.C);
}

#endif /* SMK_RECOMP_OPS_H */
