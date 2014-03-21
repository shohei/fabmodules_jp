#
#-*- coding:utf-8 -*-
# fab_mods.py
#    fab module definitions
#
# Neil Gershenfeld 9/1/13
# (c) Massachusetts Institute of Technology 2013
#
# This work may be reproduced, modified, distributed,
# performed, and displayed for any purpose, but must
# acknowledge the fab modules project. Copyright is
# retained and must be preserved. The work is provided
# as is; no warranty is provided, and users accept all 
# liability.
#
# imports
#
import wx,sys,os
#
# set workflows
#
def set_workflows(frame,formats,workflows):
   frame.formats.Append("画像 (.png)")
   formats.append(".png")
   frame.formats.Append("ボリューム (.gif)")
   formats.append(".gif")
   frame.formats.Append("メッシュ (.stl)")
   formats.append(".stl")
   frame.formats.Append("描画 (.svg)")
   formats.append(".svg")
   frame.formats.Append("プログラム (.cad)")
   formats.append(".cad")
   frame.formats.Append("数式 (.math)")
   formats.append(".math")
   #
   frame.processes.Append("画像 (.png)")
   workflows[u"画像 (.png) : 画像 (.png)"] = "make_png_png"
   workflows["design (.cad) : image (.png)"] = "make_cad_png"
   workflows[u"メッシュ (.stl) : 画像 (.png)"] = "make_stl_png"
   #
   frame.processes.Append("Encapsulated PostScript (.eps)")
   workflows[u"画像 (.png) : Encapsulated PostScript (.eps)"] = "make_png_eps"
   workflows["design (.cad) : Encapsulated PostScript (.eps)"] = "make_cad_eps"
   workflows[u"数式 (.math) : Encapsulated PostScript (.eps)"] = "make_math_eps"
   frame.processes.Append("PostScript ハーフトーン (.eps)")
   workflows[u"画像 (.png) : PostScript halftone (.eps)"] = "make_png_eps_halftone"
   #
   frame.processes.Append("DXF (.dxf)")
   workflows[u"画像 (.png) : DXF (.dxf)"] = "make_png_dxf"
   workflows["design (.cad) : DXF (.dxf)"] = "make_cad_dxf"
   workflows[u"数式 (.math) : DXF (.dxf)"] = "make_math_dxf"
   #
   frame.processes.Append("ガーバー (.grb)")
   workflows[u"画像 (.png) : ガーバー (.grb)"] = "make_png_grb"
   workflows["design (.cad) : Gerber (.grb)"] = "make_cad_grb"
   workflows[u"数式 (.math) : ガーバー (.grb)"] = "make_math_grb"
   #
   frame.processes.Append("Excellon (.drl)")
   workflows[u"画像 (.png) : Excellon (.drl)"] = "make_png_drl"
   workflows["design (.cad) : Excellon (.drl)"] = "make_cad_drl"
   workflows[u"数式 (.math) : Excellon (.drl)"] = "make_math_drl"
   #
   frame.processes.Append("Epilog レーザーカッター (.epi)")
   workflows[u"画像 (.png) : Epilog レーザーカッター (.epi)"] = "make_png_epi"
   workflows["design (.cad) : Epilog lasercutter (.epi)"] = "make_cad_epi"
   workflows[u"数式 (.math) : Epilog レーザーカッター (.epi)"] = "make_math_epi"
   workflows["描画 (.svg) : Epilog レーザーカッター (.epi)"] = "make_svg_epi"
   frame.processes.Append("Epilog ハーフトーン (.epi)")
   workflows[u"画像 (.png) : Epilog ハーフトーン (.epi)"] = "make_png_epi_halftone"
   #
   frame.processes.Append("Universal レーザーカッター (.uni)")
   workflows[u"画像 (.png) : Universal レーザーカッター (.uni)"] = "make_png_uni"
   workflows["design (.cad) : Universal lasercutter (.uni)"] = "make_cad_uni"
   workflows[u"数式 (.math) : Universal レーザーカッター (.uni)"] = "make_math_uni"
   workflows[u"描画 (.svg) : Universal レーザーカッター (.uni)"] = "make_svg_uni"
   #
   frame.processes.Append("Universal ハーフトーン (.uni)")
   workflows[u"画像 (.png) : Universal ハーフトーン (.uni)"] = "make_png_uni_halftone"
   #
   frame.processes.Append("Resonetics エキシマレーザー (.oms)")
   workflows[u"画像 (.png) : Resonetics エキシマレーザー (.oms)"] = "make_png_oms"
   workflows[u"描画 (.svg) : Resonetics エキシマレーザー (.oms)"] = "make_svg_oms"
   #
   frame.processes.Append("Omax ウォータージェット (.ord)")
   workflows[u"画像 (.png) : Omax ウォータージェット (.ord)"] = "make_png_ord"
   workflows["design (.cad) : Omax waterjet (.ord)"] = "make_cad_ord"
   workflows[u"数式 (.math) : Omax ウォータージェット (.ord)"] = "make_math_ord"
   workflows[u"描画 (.svg): Omax ウォータージェット (.ord)"] = "make_svg_ord"
   #
   frame.processes.Append("メッシュ (.stl)")
   workflows["design (.cad) : mesh (.stl)"] = "make_cad_stl"
   workflows[u"数式 (.math) : メッシュ (.stl)"] = "make_math_stl"
   #
   frame.processes.Append("Roland ビニールカッター (.camm)")
   workflows[u"画像 (.png) : Roland ビニールカッター (.camm)"] = "make_png_camm"
   workflows["design (.cad) : Roland vinylcutter (.camm)"] = "make_cad_camm"
   workflows[u"数式 (.math) : Roland ビニールカッター (.camm)"] = "make_math_camm"
   workflows[u"描画 (.svg) : Roland ビニールカッター (.camm)"] = "make_svg_camm"
   #
   frame.processes.Append("Roland モデラ (.rml)")
   workflows[u"画像 (.png) : Roland モデラ (.rml)"] = "make_png_rml"
   workflows["design (.cad) : Roland Modela (.rml)"] = "make_cad_rml"
   workflows[u"数式 (.math) : Roland モデラ (.rml)"] = "make_math_rml"
   workflows[u"メッシュ (.stl) : Roland モデラ (.rml)"] = "make_stl_rml"
   workflows[u"描画 (.svg) : Roland モデラ (.rml)"] = "make_svg_rml"
   workflows[u"画像 (.png) : Roland モデラ (.rml)"] = "make_png_rml"
   #
   frame.processes.Append("Gコード (.g)")
   workflows[u"画像 (.png) : Gコード (.g)"] = "make_png_g"
   workflows["design (.cad) : G-codes (.g)"] = "make_cad_g"
   workflows[u"数式 (.math) : Gコード (.g)"] = "make_math_g"
   workflows[u"メッシュ (.stl) : Gコード (.g)"] = "make_stl_g"
   workflows[u"描画 (.svg) : Gコード (.g)"] = "make_svg_g"
   #
   frame.processes.Append("ShopBot (.sbp)")
   workflows[u"画像 (.png) : ShopBot (.sbp)"] = "make_png_sbp"
   workflows["design (.cad) : ShopBot (.sbp)"] = "make_cad_sbp"
   workflows[u"数式 (.math) : ShopBot (.sbp)"] = "make_math_sbp"
   workflows[u"メッシュ (.stl) : ShopBot (.sbp)"] = "make_stl_sbp"
   workflows[u"描画 (.svg) : ShopBot (.sbp)"] = "make_svg_sbp"
   #
   frame.processes.Append("MTM Snap")
   workflows[u"画像 (.png) : MTM Snap"] = "make_png_snap"
   workflows["design (.cad) : MTM Snap"] = "make_cad_snap"
   workflows[u"メッシュ (.stl) : MTM Snap"] = "make_stl_snap"
   workflows[u"描画 (.svg) : MTM Snap"] = "make_svg_snap"
