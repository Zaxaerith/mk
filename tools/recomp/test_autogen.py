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
    def test_indirect_opcodes_are_two_bytes(self):
        # Every direct-page/stack indirect mode has one operand byte.  A bad
        # opcode-table size silently shifts the entire following CFG.
        opcodes = [0xA1, 0xB2, 0xB1, 0xA7, 0xB7, 0xA3, 0xB3]
        for opcode in opcodes:
            rom = bytearray(512 * 1024)
            rom[0x8100:0x8103] = bytes([opcode, 0x20, 0x6B])
            insn, _, _ = autogen._decode_at(rom, 0x80, 0x8100, False, False)
            self.assertEqual(insn["total"], 2, hex(opcode))

    def test_indirect_load_effective_addresses(self):
        source = generate([
            0xA1, 0x10,  # LDA ($10,X)
            0xB2, 0x11,  # LDA ($11)
            0xB1, 0x12,  # LDA ($12),Y
            0xA7, 0x13,  # LDA [$13]
            0xB7, 0x14,  # LDA [$14],Y
            0xA3, 0x15,  # LDA $15,S
            0xB3, 0x16,  # LDA ($16,S),Y
            0x6B,
        ])
        for mode in ("dpxi", "dpi", "dpiy", "dpil", "dpily", "sr", "sriy"):
            self.assertIn(f"smk_ea_{mode}", source)
        self.assertEqual(source.count("smk_bus_read16_24"), 7)

    def test_indirect_store_effective_addresses(self):
        source = generate([
            0x81, 0x10, 0x92, 0x11, 0x91, 0x12, 0x87, 0x13,
            0x97, 0x14, 0x83, 0x15, 0x93, 0x16, 0x6B,
        ], p=0x20)
        self.assertEqual(source.count("smk_bus_write8_24"), 7)

    def test_mid_function_entry_jumps_to_real_entry_block(self):
        # $8103 BRA $8100; the lower block is shared code before the entry.
        rom = bytearray(512 * 1024)
        rom[0x8100:0x8105] = bytes([0xA6, 0x4A, 0x60, 0x80, 0xFB])
        source = autogen.generate(rom, 0x80, 0x8103, 0x00, "smk_test")
        entry_jump = source.index("goto L_8103_M0X0;")
        lower_block = source.index("L_8100_M0X0:;")
        self.assertLess(entry_jump, lower_block)

    def test_cfg_keeps_distinct_mx_variants_for_one_pc(self):
        # BEQ selects SEP or REP before both paths merge at a width-neutral NOP.
        source = generate([
            0xF0, 0x04,       # BEQ $8106
            0xC2, 0x20,       # REP #$20
            0x80, 0x02,       # BRA $8108
            0xE2, 0x20,       # SEP #$20
            0xEA,             # same PC under M=0 and M=1
            0x6B,
        ], p=0x20)
        self.assertIn("L_8108_M0X0", source)
        self.assertIn("L_8108_M1X0", source)
        self.assertEqual(source.count("/* $8108 NOP */"), 2)

    def test_branch_cycles_are_path_dependent(self):
        source = generate([0xF0, 0x01, 0xEA, 0x6B])
        self.assertIn("if (g_cpu.flag_Z) { recomp_tick(6);", source)
        self.assertEqual(source.count("recomp_tick(6);"), 1)

        bra = generate([0x80, 0x01, 0xEA, 0x6B])
        self.assertIn("recomp_tick(6);", bra)
        self.assertIn("goto L_8103_M0X0", bra)

    def test_multi_entry_dispatches_from_live_mx_flags(self):
        rom = bytearray(512 * 1024)
        rom[0x8100:0x8102] = bytes([0xEA, 0x6B])
        source = autogen.generate(rom, 0x80, 0x8100,
                                  [0x00, 0x10, 0x20, 0x30], "smk_test")
        self.assertIn("g_cpu.flag_M == 0", source)
        self.assertIn("g_cpu.flag_X == 0", source)
        for m in (0, 1):
            for x in (0, 1):
                self.assertIn(f"goto L_8100_M{m}X{x};", source)
                self.assertIn(f"L_8100_M{m}X{x}:;", source)
        self.assertEqual(source.count("/* $8100 NOP */"), 4)

    def test_exact_profile_variants_avoid_impossible_entry_width(self):
        # X=16 is a calling convention here. Decoding X=8 would consume only
        # one immediate byte and mistake the high byte ($00) for BRK.
        rom = bytearray(512 * 1024)
        rom[0x8100:0x8105] = bytes([0xA2, 0x34, 0x00, 0xEA, 0x6B])
        source = autogen.generate(rom, 0x80, 0x8100, [0x00, 0x20], "smk_test")
        self.assertIn("L_8100_M0X0", source)
        self.assertIn("L_8100_M1X0", source)
        self.assertNotIn("L_8100_M0X1", source)
        self.assertEqual(source.count("BRK"), 0)

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

    def test_block_moves_repeat_and_honor_index_width(self):
        mvn = generate([0x54, 0x7F, 0x7E, 0x6B])
        self.assertIn("do { recomp_tick(", mvn)
        self.assertIn("bus_read8(0x7E, g_cpu.X)", mvn)
        self.assertIn("bus_write8(0x7F, g_cpu.Y", mvn)
        self.assertIn("g_cpu.DB = 0x7F", mvn)
        self.assertIn("g_cpu.X + 1", mvn)
        self.assertNotIn("g_cpu.X &= 0x00FF", mvn)

        mvp8 = generate([0x44, 0x7E, 0x7F, 0x6B], p=0x10)
        self.assertIn("g_cpu.X - 1", mvp8)
        self.assertIn("g_cpu.X &= 0x00FF", mvp8)
        self.assertIn("while (g_cpu.C != 0xFFFF)", mvp8)

    def test_remaining_register_transfers(self):
        source = generate([0xBA, 0x9A, 0x9B, 0xBB, 0x5B, 0x7B,
                           0x1B, 0x3B, 0x6B])
        self.assertIn("g_cpu.S & 0xFF00", source)  # TXS handles 8-bit X safely
        self.assertIn("g_cpu.DP = g_cpu.C", source)
        self.assertIn("g_cpu.C = g_cpu.DP", source)
        self.assertIn("g_cpu.C = g_cpu.S", source)


if __name__ == "__main__":
    unittest.main()
