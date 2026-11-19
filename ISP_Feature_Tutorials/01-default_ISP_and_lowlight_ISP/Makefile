CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Werror -Wno-unknown-pragmas -Ireference_files/cpp/include -Ireference_files/cpp/tests
PYTHON ?= python3
BUILD := build

.PHONY: all test cpp-test py-test golden-check clean

all: test

test: cpp-test py-test golden-check

$(BUILD):
	mkdir -p $(BUILD)

cpp-test: | $(BUILD)
	$(CXX) $(CXXFLAGS) reference_files/cpp/src/default_isp.cpp reference_files/cpp/tests/test_default_isp_csim.cpp -o $(BUILD)/default_isp_csim
	./$(BUILD)/default_isp_csim reference_files/cpp/tests/default_isp_golden_vectors.csv
	$(CXX) $(CXXFLAGS) reference_files/cpp/src/lowlight_isp.cpp reference_files/cpp/tests/test_lowlight_isp_csim.cpp -o $(BUILD)/lowlight_isp_csim
	./$(BUILD)/lowlight_isp_csim reference_files/cpp/tests/lowlight_isp_golden_vectors.csv

py-test:
	cd reference_files/python && $(PYTHON) verify_new_arm_pipelines.py

# Python이 다시 만든 골든 벡터가 저장소의 골든 CSV와 바이트 단위로 같은지 확인
golden-check: | $(BUILD)
	cd reference_files/python && $(PYTHON) gen_default_isp_golden.py --out ../../$(BUILD)/default_golden.csv
	cd reference_files/python && $(PYTHON) gen_lowlight_isp_golden.py --out ../../$(BUILD)/lowlight_golden.csv
	cmp $(BUILD)/default_golden.csv reference_files/cpp/tests/default_isp_golden_vectors.csv
	cmp $(BUILD)/lowlight_golden.csv reference_files/cpp/tests/lowlight_isp_golden_vectors.csv

clean:
	rm -rf $(BUILD)
