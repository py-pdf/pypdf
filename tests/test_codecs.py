"""Test LZW-related code."""
from pathlib import Path

import pytest

from pypdf._codecs._codecs import LzwCodec

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"

test_cases = [
    pytest.param(b"", id="Empty input"),
    pytest.param(b"A", id="Single character"),
    pytest.param(b"AAAAAA", id="Repeating character"),
    pytest.param(b"Hello, World!", id="Simple text"),
    pytest.param(b"ABABABABABAB", id="Repeating pattern"),
    pytest.param(b"The quick brown fox jumps over the lazy dog", id="Longer text"),
    pytest.param(b"\x00\xFF\x00\xFF", id="Binary data"),
    pytest.param(
        b"BBBCBDBEBFBGBHBIBJBKBLBMBNBOBPBQBRBSBTBUBVBWBXBYBZB[B\\B]B^B_B`BaBbBcBdBeBfBgBhBiBjBkBlBmBnBoBpBqBrBsBtBuBvBwBxByCBCCCDCECFCGCHCICJCKCLCMCNCOCPCQCRCSCTCUCVCWCXCYCZC[C\\C]C^C_C`CaCbCcCdCeCfCgChCiCjCkClCmCnCoCpCqCrCsCtCuCvCwCxCyDBDCDDDEDFDGDHDIDJDKDLDMDNDODPDQDRDSDTDUDVDWDXDYDZD[D\\D]D^D_D`DaDbDcDdDeDfDgDhDiDjDkDlDmDnDoDpDqDrDsDtDuDvDwDxDyEBECEDEEEFEGEHEIEJEKELEMENEOEPEQERESETEUEVEWEXEYEZE[E\\E]E^E_E`EaEbEcEdEeEfEgEhEiEjEkElEmEnEoEpEqErEsEtEuEvEwExEyFBFCFDFEFFFGFHFIFJFKFLFMFNFOFPFQFRFSFTFUFVFWFXFYFZF[F\\F]F^F_F`FaFbFcFdFeFfFgFhFiFjFkFlFmFnFoFpFqFrFsFtFuFvFwFxFyGBGCGDGEGFGGGHGIGJGKGLGMGNGOGPGQGRGSGTGUGVGWGXGYGZG[G\\G]G^G_G`GaGbGcGdGeGfGgGhGiGjGkGlGmGnGoGpGqGrGsGtGuGvGwGxGyHBHCHDHEHFHGHHHIHJHKHLHMHNHOHPHQHRHSHTHUHVHWHXHYHZH[H\\H]H^H_H`HaHbHcHdHeHfHgHhHiHjHkHlHmHnHoHpHqHrHsHtHuHvHwHxHyIBICIDIEIFIGIHIIIJIKILIMINIOIPIQIRISITIUIVIWIXIYIZI[I\\I]I^I_I`IaIbIcIdIeIfIgIhIiIjIkIlImInIoIpIqIrIsItIuIvIwIxIyJBJCJDJEJFJGJHJIJJJKJLJMJNJOJPJQJRJSJTJUJVJWJXJYJZJ[J\\J]J^J_J`JaJbJcJdJeJfJgJhJiJjJkJlJmJnJoJpJqJrJsJtJuJvJwJxJyKBKCKDKEKFKGKHKIKJKKKLKMKNKOKPKQKRKSKTKUKVKWKXKYKZK[K\\K]K^K_K`KaKbKcKdKeKfKgKhKiKjKkKlKmKnKoKpKqKrKsKtKuKvKwKxKyLBLCLDLELFLGLHLILJLKLLLMLNLOLPLQLRLSLTLULVLWLXLYLZL[L\\L]L^L_L`LaLbLcLdLeLfLgLhLiLjLkLlLmLnLoLpLqLrLsLtLuLvLwLxLyMBMCMDMEMFMGMHMIMJMKMLMMMNMOMPMQMRMSMTMUMVMWMXMYMZM[M\\M]M^M_M`MaMbMcMdMeMfMgMhMiMjMkMlMmMnMoMpMqMrMsMtMuMvMwMxMyNBNCNDNENFNGNHNINJNKNLNMNNNONPNQNRNSNTNUNVNWNXNYNZN[N\\N]N^N_N`NaNbNcNdNeNfNgNhNiNjNkNlNmNnNoNpNqNrNsNtNuNvNwNxNyOBOCODOEOFOGOHOIOJOKOLOMONOOOPOQOROSOTOUOVOWOXOYOZO[O\\O]O^O_O`OaObOcOdOeOfOgOhOiOjOkOlOmOnOoOpOqOrOsOtOuOvOwOxOyPBPCPDPEPFPGPHPIPJPKPLPMPNPOPPPQPRPSPTPUPVPWPXPYPZP[P\\P]P^P_P`PaPbPcPdPePfPgPhPiPjPkPlPmPnPoPpPqPrPsPtPuPvPwPxPyQBQCQDQEQFQGQHQIQJQKQLQMQNQOQPQQQRQSQTQUQVQWQXQYQZQ[Q\\Q]Q^Q_Q`QaQbQcQdQeQfQgQhQiQjQkQlQmQnQoQpQqQrQsQtQuQvQwQxQyRBRCRDRERFRGRHRIRJRKRLRMRNRORPRQRRRSRTRURVRWRXRYRZR[R\\R]R^R_R`RaRbRcRdReRfRgRhRiRjRkRlRmRnRoRpRqRrRsRtRuRvRwRxRySBSCSDSESFSGSHSISJSKSLSMSNSOSPSQSRSSSTSUSVSWSXSYSZS[S\\S]S^S_S`SaSbScSdSeSfSgShSiSjSkSlSmSnSoSpSqSrSsStSuSvSwSxSyTBTCTDTETFTGTHTITJTKTLTMTNTOTPTQTRTSTTTUTVTWTXTYTZT[T\\T]T^T_T`TaTbTcTdTeTfTgThTiTjTkTlTmTnToTpTqTrTsTtTuTvTwTxTyUBUCUDUEUFUGUHUIUJUKULUMUNUOUPUQURUSUTUUUVUWUXUYUZU[U\\U]U^U_U`UaUbUcUdUeUfUgUhUiUjUkUlUmUnUoUpUqUrUsUtUuUvUwUxUyVBVCVDVEVFVGVHVIVJVKVLVMVNVOVPVQVRVSVTVUVVVWVXVYVZV[V\\V]V^V_V`VaVbVcVdVeVfVgVhViVjVkVlVmVnVoVpVqVrVsVtVuVvVwVxVyWBWCWDWEWFWGWHWIWJWKWLWMWNWOWPWQWRWSWTWUWVWWWXWYWZW[W\\W]W^W_W`WaWbWcWdWeWfWgWhWiWjWkWlWmWnWoWpWqWrWsWtWuWvWwWxWyXBXCXDXEXFXGXHXIXJXKXLXMXNXOXPXQXRXSXTXUXVXWXXXYXZX[X\\X]X^X_X`XaXbXcXdXeXfXgXhXiXjXkXlXmXnXoXpXqXrXsXtXuXvXwXxXyYBYCYDYEYFYGYHYIYJYKYLYMYNYOYPYQYRYSYTYUYVYWYXYYYZY[Y\\Y]Y^Y_Y`YaYbYcYdYeYfYgYhYiYjYkYlYmYnYoYpYqYrYsYtYuYvYwYxYyZBZCZDZEZFZGZHZIZJZKZLZMZNZOZPZQZRZSZTZUZVZWZXZYZZZ[Z\\Z]Z^Z_Z`ZaZbZcZdZeZfZgZhZiZjZkZlZmZnZoZpZqZrZsZtZuZvZwZxZy[B[C[D[E[F[G[H[I[J[K[L[M[N[O[P[Q[R[S[T[U[V[W[X[Y[Z[[[\\[][^[_[`[a[b[c[d[e[f[g[h[i[j[k[l[m[n[o[p[q[r[s[t[u[v[w[x[y\\B\\C\\D\\E\\F\\G\\H\\I\\J\\K\\L\\M\\N\\O\\P\\Q\\R\\S\\T\\U\\V\\W\\X\\Y\\Z\\[\\\\\\]\\^\\_\\`\\a\\b\\c\\d\\e\\f\\g\\h\\i\\j\\k\\l\\m\\n\\o\\p\\q\\r\\s\\t\\u\\v\\w\\x\\y]B]C]D]E]F]G]H]I]J]K]L]M]N]O]P]Q]R]S]T]U]V]W]X]Y]Z][]\\]]]^]_]`]a]b]c]d]e]f]g]h]i]j]k]l]m]n]o]p]q]r]s]t]u]v]w]x]y^B^C^D^E^F^G^H^I^J^K^L^M^N^O^P^Q^R^S^T^U^V^W^X^Y^Z^[^\\^]^^^_^`^a^b^c^d^e^f^g^h^i^j^k^l^m^n^o^p^q^r^s^t^u^v^w^x^y_B_C_D_E_F_G_H_I_J_K_L_M_N_O_P_Q_R_S_T_U_V_W_X_Y_Z_[_\\_]_^___`_a_b_c_d_e_f_g_h_i_j_k_l_m_n_o_p_q_r_s_t_u_v_w_x_y`B`C`D`E`F`G`H`I`J`K`L`M`N`O`P`Q`R`S`T`U`V`W`X`Y`Z`[`\\`]`^`_```a`b`c`d`e`f`g`h`i`j`k`l`m`n`o`p`q`r`s`t`u`v`w`x`yaBaCaDaEaFaGaHaIaJaKaLaMaNaOaPaQaRaSaTaUaVaWaXaYaZa[a\\a]a^a_a`aaabacadaeafagahaiajakalamanaoapaqarasatauavawaxaybBbCbDbEbFbGbHbIbJbKbLbMbNbObPbQbRbSbTbUbVbWbXbYbZb[b\\b]b^b_b`babbbcbdbebfbgbhbibjbkblbmbnbobpbqbrbsbtbubvbwbxbycBcCcDcEcFcGcHcIcJcKcLcMcNcOcPcQcRcScTcUcVcWcXcYcZc[c\\c]c^c_c`cacbcccdcecfcgchcicjckclcmcncocpcqcrcsctcucvcwcxcydBdCdDdEdFdGdHdIdJdKdLdMdNdOdPdQdRdSdTdUdVdWdXdYdZd[d\\d]d^d_d`dadbdcdddedfdgdhdidjdkdldmdndodpdqdrdsdtdudvdwdxdyeBeCeDeEeFeGeHeIeJeKeLeMeNeOePeQeReSeTeUeVeWeXeYeZe[e\\e]e^e_e`eaebecedeeefegeheiejekelemeneoepeqereseteuevewexeyfBfCfDfEfFfGfHfIfJfKfLfMfNfOfPfQfRfSfTfUfVfWfXfYfZf[f\\f]f^f_f`fafbfcfdfefffgfhfifjfkflfmfnfofpfqfrfsftfufvfwfxfygBgCgDgEgFgGgHgIgJgKgLgMgNgOgPgQgRgSgTgUgVgWgXgYgZg[g\\g]g^g_g`gagbgcgdgegfggghgigjgkglgmgngogpgqgrgsgtgugvgwgxgyhBhChDhEhFhGhHhIhJhKhLhMhNhOhPhQhRhShThUhVhWhXhYhZh[h\\h]h^h_h`hahbhchdhehfhghhhihjhkhlhmhnhohphqhrhshthuhvhwhxhyiBiCiDiEiFiGiHiIiJiKiLiMiNiOiPiQiRiSiTiUiViWiXiYiZi[i\\i]i^i_i`iaibicidieifigihiiijikiliminioipiqirisitiuiviwixiyjBjCjDjEjFjGjHjIjJjKjLjMjNjOjPjQjRjSjTjUjVjWjXjYjZj[j\\j]j^j_j`jajbjcjdjejfjgjhjijjjkjljmjnjojpjqjrjsjtjujvjwjxjykBkCkDkEkFkGkHkIkJkKkLkMkNkOkPkQkRkSkTkUkVkWkXkYkZk[k\\k]k^k_k`kakbkckdkekfkgkhkikjkkklkmknkokpkqkrksktkukvkwkxkylBlClDlElFlGlHlIlJlKlLlMlNlOlPlQlRlSlTlUlVlWlXlYlZl[l\\l]l^l_l`lalblcldlelflglhliljlklllmlnlolplqlrlsltlulvlwlxlymBmCmDmEmFmGmHmImJmKmLmMmNmOmPmQmRmSmTmUmVmWmXmYmZm[m\\m]m^m_m`mambmcmdmemfmgmhmimjmkmlmmmnmompmqmrmsmtmumvmwmxmynBnCnDnEnFnGnHnInJnKnLnMnNnOnPnQnRnSnTnUnVnWnXnYnZn[n\\n]n^n_n`nanbncndnenfngnhninjnknlnmnnnonpnqnrnsntnunvnwnxnyoBoCoDoEoFoGoHoIoJoKoLoMoNoOoPoQoRoSoToUoVoWoXoYoZo[o\\o]o^o_o`oaobocodoeofogohoiojokolomonooopoqorosotouovowoxoypBpCpDpEpFpGpHpIpJpKpLpMpNpOpPpQpRpSpTpUpVpWpXpYpZp[p\\p]p^p_p`papbpcpdpepfpgphpipjpkplpmpnpopppqprpsptpupvpwpxpyqBqCqDqEqFqGqHqIqJqKqLqMqNqOqPqQqRqSqTqUqVqWqXqYqZq[q\\q]q^q_q`qaqbqcqdqeqfqgqhqiqjqkqlqmqnqoqpqqqrqsqtquqvqwqxqyrBrCrDrErFrGrHrIrJrKrLrMrNrOrPrQrRrSrTrUrVrWrXrYrZr[r\\r]r^r_r`rarbrcrdrerfrgrhrirjrkrlrmrnrorprqrrrsrtrurvrwrxrysBsCsDsEsFsGsHsIsJsKsLsMsNsOsPsQsRsSsTsUsVsWsXsYsZs[s\\s]s^s_s`sasbscsdsesfsgshsisjskslsmsnsospsqsrssstsusvswsxsytBtCtDtEtFtGtHtItJtKtLtMtNtOtPtQtRtStTtUtVtWtXtYtZt[t\\t]t^t_t`tatbtctdtetftgthtitjtktltmtntotptqtrtstttutvtwtxtyuBuCuDuEuFuGuHuIuJuKuLuMuNuOuPuQuRuSuTuUuVuWuXuYuZu[u\\u]u^u_u`uaubucudueufuguhuiujukulumunuoupuqurusutuuuvuwuxuyvBvCvDvEvFvGvHvIvJvKvLvMvNvOvPvQvRvSvTvUvVvWvXvYvZv[v\\v]v^v_v`vavbvcvdvevfvgvhvivjvkvlvmvnvovpvqvrvsvtvuvvvwvxvywBwCwDwEwFwGwHwIwJwKwLwMwNwOwPwQwRwSwTwUwVwWwXwYwZw[w\\w]w^w_w`wawbwcwdwewfwgwhwiwjwkwlwmwnwowpwqwrwswtwuwvwwwxwyxBxCxDxExFxGxHxIxJxKxLxMxNxOxPxQxRxSxTxUxVxWxXxYxZx[x\\x]x^x_x`xaxbxcxdxexfxgxhxixjxkxlxmxnxoxpxqxrxsxtxuxvxwxxxyyByCyDyEyFyGyHyIyJyKyLyMyNyOyPyQyRySyTyUyVyWyXyYyZy[y\\y]y^y_y`yaybycydyeyfygyhyiyjykylymynyoypyqyrysytyuyvywyxyyBBBBBCBBDBBEBBFBBGBBHBBIBBJBBKBBLBBMBBNBBOBBPBBQBBRBBSBBTBBUBBVBBWBBXBBYBBZBB[BB\\BB]BB^BB_BB`BBaBBbBBcBBdBBeBBfBBgBBhBBiBBjBBkBBlBBmBBnBBoBBpBBqBBrBBsBBtBBuBBvBBwBBxBByBCBBCCBCDBCEBCFBCGBCHBCIBCJBCKBCLBCMBCNBCOBCPBCQBCRBCSBCTBCUBCVBCWBCXBCYBCZBC[BC\\BC]BC^BC_BC`BCaBCbBCcBCdBCeBCfBCgBChBCiBCjBCkBClBCmBCnBCoBCpBCqBCrBCsBCtBCuBCvBCwBCxBCyBDBBDCBDDBDEBDFBDGBDHBDIBDJBDKBDLBDMBDNBDOBDPBDQBDRBDSBDTBDUBDVBDWBDXBDYBDZBD[BD\\BD]BD^BD_BD`BDaBDbBDcBDdBDeBDfBDgBDhBDiBDjBDkBDlBDmBDnBDoBDpBDqBDrBDsBDtBDuBDvBDwBDxBDyBEBBECBEDBEEBEFBEGBEHBEIBEJBEKBELBEMBENBEOBEPBEQBERBESBETBEUBEVBEWBEXBEYBEZBE[BE\\BE]BE^BE_BE`BEaBEbBEcBEdBEeBEfBEgBEhBEiBEjBEkBElBEmBEnBEoBEpBEqBErBEsBEtBEuBEvBEwBExBEyBFBBFCBFDBFEBFFBFGBFHBFIBFJBFKBFLBFMBFNBFOBFPBFQBFRBFSBFTBFUBFVBFWBFXBFYBFZBF[BF\\BF]BF^BF_BF`BFaBFbBFcBFdBFeBFfBFgBFhBFiBFjBFkBFlBFmBFnBFoBFpBFqBFrBFsBFtBFuBFvBFwBFxBFyBGBBGCBGDBGEBGFBGGBGHBGIBGJBGKBGLBGMBGNBGOBGPBGQBGRBGSBGTBGUBGVBGWBGXBGYBGZBG[BG\\BG]BG^BG_BG`BGaBGbBGcBGdBGeBGfBGgBGhBGiBGjBGkBGlBGmBGnBGoBGpBGqBGrBGsBGtBGuBGvBGwBGxBGyBHBBHCBHDBHEBHFBHGBHHBHIBHJBHKBHLBHMBHNBHOBHPBHQBHRBHSBHTBHUBHVBHWBHXBHYBHZBH[BH\\BH]BH^BH_BH`BHaBHbBHcBHdBHeBHfBHgBHhBHiBHjBHkBHlBHmBHnBHoBHpBHqBHrBHsBHtBHuBHvBHwBHxBHyBIBBICBIDBIEBIFBIGBIHBIIBIJBIKBILBIMBINBIOBIPBIQBIRBISBITBIUBIVBIWBIXBIYBIZBI[BI\\BI]BI^BI_BI`BIaBIbBIcBIdBIeBIfBIgBIhBIiBIjBIkBIlBImBInBIoBIpBIqBIrBIsBItBIuBIvBIwBIxBIyBJBBJCBJDBJEBJFBJGBJHBJIBJJBJKBJLBJMBJNBJOBJPBJQBJRBJSBJTBJUBJVBJWBJXBJYBJZBJ[BJ\\BJ]BJ^BJ_BJ`BJaBJbBJcBJdBJeBJfBJgBJhBJiBJjBJkBJlBJmBJnBJoBJpBJqBJrBJsBJtBJuBJvBJwBJxBJyBKBBKCBKDBKEBKFBKGBKHBKIBKJBKKBKLBKMBKNBKOBKPBKQBKRBKSBKTBKUBKVBKWBKXBKYBKZBK[BK\\BK]BK^BK_BK`BKaBKbBKcBKdBKeBKfBKgBKhBKiBKjBKkBKlBKmBKnBKoBKpBKqBKrBKsBKtBKuBKvBKwBKxBKyBLBBLCBLDBLEBLFBLGBLHBLIBLJBLKBLLBLMBLNBLOBLPBLQBLRBLSBLTBLUBLVBLWBLXBLYBLZBL[BL\\BL]BL^BL_BL`BLaBLbBLcBLdBLeBLfBLgBLhBLiBLjBLkBLlBLmBLnBLoBLpBLqBLrBLsBLtBLuBLvBLwBLxBLyBMBBMCBMDBMEBMFBMGBMHBMIBMJBMKBMLBMMBMNBMOBMPBMQBMRBMSBMTBMUBMVBMWBMXBMYBMZBM[BM\\BM]BM^BM_BM`BMaBMbBMcBMdBMeBMfBMgBMhBMiBMjBMkBMlBMmBMnBMoBMpBMqBMrBMsBMtBMuBMvBMwBMxBMyBNBBNCBNDBNEBNFBNGBNHBNIBNJBNKBNLBNMBNNBNOBNPBNQBNRBNSBNTBNUBNVBNWBNXBNYBNZBN[BN\\BN]BN^BN_",
        id="Table overflow",
    ),
]


@pytest.mark.parametrize("data", test_cases)
def test_encode_decode(data):
    """Decoder and encoder match."""
    codec = LzwCodec()
    compressed_data = codec.encode(data)
    decoded = codec.decode(compressed_data)
    assert decoded == data


@pytest.mark.parametrize(
    ("plain", "expected_encoded"),
    [
        (b"", b"\x80@@"),
        (b"A", b"\x80\x10` "),
        (b"AAAAAA", b"\x80\x10`P8\x08"),
        (b"Hello, World!", b"\x80\x12\x0c\xa6\xc3a\xbcX +\x9b\xceF\xc3 \x86\x02"),
    ],
)
def test_encode_lzw(plain, expected_encoded):
    codec = LzwCodec()
    actual_encoded = codec.encode(plain)
    assert actual_encoded == expected_encoded


@pytest.mark.parametrize(
    ("encoded", "expected_decoded"),
    [
        # _pack_codes_into_bytes([256, 65, 66, 67, 68, 256, 256, 69, 70, 71, 72, 257])
        (b"\x80\x10HD2$\x02\x00E#\x11\xc9\x10\x10", b"ABCDEFGH"),  # Clear twice.
        # _pack_codes_into_bytes([65, 66, 67, 68, 257])
        (b" \x90\x88dH\x08", b"ABCD"),  # No explicit initial clear marker.
    ],
)
def test_decode_lzw(encoded, expected_decoded):
    codec = LzwCodec()
    actual_decoded = codec.decode(encoded)
    assert actual_decoded == expected_decoded


def test_lzw_decoder_table_overflow(caplog):
    path = RESOURCE_ROOT / "lzw_decoder_table_overflow.bin"
    codec = LzwCodec()
    assert codec.decode(path.read_bytes()).startswith(
        b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@'
    )
    assert len(codec.decoding_table) == 4096
    assert "Ignoring too large LZW table index." in caplog.text
