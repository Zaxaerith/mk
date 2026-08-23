#!/usr/bin/env python3
"""Unit tests for width-sensitive 65816 code generation."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import autogen  # noqa: E402


def generate(code, p=0x00, addr=0x8100):
    """Generate one synthetic function in bank $80's FastROM window."""
    rom = bytearray(512 * 1024)
    rom[addr:addr + len(code)] = bytes(code)
    return autogen.generate(rom, 0x80, addr, p, "smk_test")


class WidthSensitiveStackTests(unittest.TestCase):
    def test_16_bit_stack_helpers_and_cycles(self):
        source = generate([0x48, 0x68, 0xDA, 0xFA, 0x5A, 0x7A, 0x6B])
        for helper in ("op_pha16", "op_pla16", "op_phx16", "op_plx16",
                       "op_phy16", "op_ply16"):
            self.assertIn(helper + "();", source)
        self.assertIn("recomp_tick(28);", source)  # 16-bit push
        self.assertIn("recomp_tick(34);", source)  # 16-bit pull

    def test_8_bit_stack_preserves_b_and_uses_one_byte(self):
        source = generate([0x48, 0x68, 0xDA, 0xFA, 0x5A, 0x7A, 0x6B], p=0x30)
        self.assertNotIn("op_pha16", source)
        self.assertNotIn("op_phx16", source)
        self.assertIn("bus_wram_write8(g_cpu.S", source)
        self.assertIn("g_cpu.C & 0xFF00", source)
        self.assertIn("recomp_tick(20);", source)  # 8-bit push
        self.assertIn("recomp_tick(26);", source)  # 8-bit pull

    def test_rep_sep_changes_following_stack_width(self):
        source = generate([0xE2, 0x30, 0x48, 0xDA, 0xC2, 0x30,
                           0x48, 0xDA, 0x6B])
        self.assertEqual(source.count("bus_wram_write8(g_cpu.S"), 2)
        self.assertIn("op_pha16();", source)
        self.assertIn("op_phx16();", source)


class AdditionalOpcodeTests(unittest.TestCase):
    def test_mid_function_entry_jumps_to_real_entry_block(self):
        # $8103 BRA $8100; the lower block is shared code before the entry.
        rom = bytearray(512 * 1024)
        rom[0x8100:0x8105] = bytes([0xA6, 0x4A, 0x60, 0x80, 0xFB])
        source = autogen.generate(rom, 0x80, 0x8103, 0x00, "smk_test")
        entry_jump = source.index("goto L_8103;")
        lower_block = source.index("L_8100:;")
        self.assertLess(entry_jump, lower_block)

    def test_bank_and_direct_page_stack_ops(self):
        source = generate([0x4B, 0x0B, 0x2B, 0x6B])  # PHK, PHD, PLD, RTL
        self.assertIn("g_cpu.PB", source)
        self.assertIn("bus_wram_write16(g_cpu.S, g_cpu.DP)", source)
        self.assertIn("g_cpu.DP = bus_wram_read16(g_cpu.S)", source)

    def test_tsb_trb_emit_read_modify_write_and_z(self):
        source = generate([0x04, 0x20, 0x14, 0x22, 0x6B])
        self.assertEqual(source.count("g_cpu.flag_Z"), 2)
        self.assertIn("_m | _a", source)
        self.assertIn("_m & (uint16_t)~_a", source)

    def test_adc_sbc_memory_width_and_nop(self):
        source16 = generate([0x65, 0x10, 0xF5, 0x20, 0xEA, 0x6B])
        self.assertIn("smk_op_adc16", source16)
        self.assertIn("smk_op_sbc16", source16)
        self.assertIn("bus_read16", source16)
        self.assertIn("(void)0;", source16)

        source8 = generate([0x65, 0x10, 0xF5, 0x20, 0x6B], p=0x20)
        self.assertIn("smk_op_adc8", source8)
        self.assertIn("smk_op_sbc8", source8)
        self.assertIn("bus_read8", source8)

    def test_remaining_register_transfers(self):
        source = generate([0xBA, 0x9A, 0x9B, 0xBB, 0x5B, 0x7B,
                           0x1B, 0x3B, 0x6B])
        self.assertIn("g_cpu.S & 0xFF00", source)  # TXS handles 8-bit X safely
        self.assertIn("g_cpu.DP = g_cpu.C", source)
        self.assertIn("g_cpu.C = g_cpu.DP", source)
        self.assertIn("g_cpu.C = g_cpu.S", source)


if __name__ == "__main__":
    unittest.main()
