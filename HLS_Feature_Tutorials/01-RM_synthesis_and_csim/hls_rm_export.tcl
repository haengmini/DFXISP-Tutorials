# RM 탑 1개를 테스트벤치 없이 합성하고 Verilog IP로 내보낸다 (dfx-reimplementation-2026-08-01.md 절차 1)
# 소스는 평평한 임시 폴더(HLS_FLAT)에 복사돼 있고, 프로젝트도 그 아래에 만든다.
# (README: 중첩된 프로젝트 경로에서 add_files 소스가 누락되는 알려진 문제의 우회)
set top  $::env(RM_TOP)
set flat $::env(HLS_FLAT)
cd $flat
open_project -reset hls_$top
set_top $top
add_files dfxisp_accel.cpp -cflags "-std=c++17 -I."
open_solution -reset solution1
set_part xczu7ev-ffvc1156-2-e
create_clock -period 5.0 -name default
csynth_design
export_design -rtl verilog -format ip_catalog
close_project
exit
