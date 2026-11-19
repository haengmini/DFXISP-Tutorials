CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Werror -Wno-unknown-pragmas -Iinclude -Itests
BUILD := build

.PHONY: all csim clean

all: csim

# 회로 소스를 일반 C++로 컴파일해 골든 벡터와 한 픽셀도 다르지 않은지 비교한다.
# 테스트가 골든 CSV를 "tests/..." 상대 경로로 찾으므로 reference_files 안에서 실행한다.
csim:
	mkdir -p reference_files/$(BUILD)
	cd reference_files && $(CXX) $(CXXFLAGS) src/dfxisp_accel.cpp tests/test_dfxisp_csim.cpp -o $(BUILD)/dfxisp_csim && ./$(BUILD)/dfxisp_csim
	cd reference_files && $(CXX) $(CXXFLAGS) src/dfxisp_rm.cpp tests/test_rm_csim.cpp -o $(BUILD)/dfxisp_rm_csim && ./$(BUILD)/dfxisp_rm_csim tests/rm_golden_vectors.csv
	cd reference_files && $(CXX) $(CXXFLAGS) src/default_isp.cpp tests/test_default_isp_csim.cpp -o $(BUILD)/default_isp_csim && ./$(BUILD)/default_isp_csim tests/default_isp_golden_vectors.csv
	cd reference_files && $(CXX) $(CXXFLAGS) src/lowlight_isp.cpp tests/test_lowlight_isp_csim.cpp -o $(BUILD)/lowlight_isp_csim && ./$(BUILD)/lowlight_isp_csim tests/lowlight_isp_golden_vectors.csv

clean:
	rm -rf reference_files/$(BUILD)
