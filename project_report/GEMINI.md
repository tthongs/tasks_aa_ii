# Project Overview: Ethernet UDP Protocol with ADT7420

This project is a comprehensive technical report titled **"Design and Implementation of Ethernet UDP Protocol using ADT7420 Temperature sensor"**. It was developed by a team of students (Georgin Roy, Sanskar Singh, Sufyan Mohammad, and Vanshika Sharma) as part of their Bachelor of Technology degree in Electronics and Communication Engineering (Session 2025-26) under the guidance of Dr. Aakriti Chhabra.

The report details the hardware/software co-design of a system that acquires temperature data from an ADT7420 sensor and transmits it over Ethernet using the UDP protocol. The system is implemented on a Xilinx/AMD FPGA (specifically referencing Basys 3 and Zynq-7000 platforms) using Vivado and Vitis design suites.

## Directory Overview

This directory serves as the repository for the project report and its associated documentation. It primarily contains the finalized Microsoft Word (`.docx`) version of the report, which has undergone several iterations of enhancement.

## Key Files

*   **`_project_report_v3.docx`**: The primary document. It is a detailed report (approx. 50+ pages) covering:
    *   **Chapter 1 (Introduction)**: Problem statement, objectives, and methodology.
    *   **Chapter 2 (Hardware Architecture)**: Details on the ADT7420 sensor, Basys 3 FPGA board, and ARM Cortex-A Processing System.
    *   **Chapter 3 (Design Flow)**: Detailed implementation steps in Vivado (PL) and Vitis (PS), including I2C communication and AXI interconnects.
    *   **Chapter 4 (Software & Literature)**: Driver initialization, data acquisition flow, and a comparative analysis of existing thermal monitoring approaches.
    *   **Chapter 5 (Conclusion)**: Summary of results and future enhancements.
    *   **Appendix**: Includes a full List of Figures and List of Tables.
    *   **References**: Key academic and technical citations.

## Usage

The contents of this directory are intended for:
1.  **Documentation Review**: Understanding the technical implementation of FPGA-based sensor interfacing and network communication.
2.  **Reference Material**: Using the comparative analysis and literature review for further research in embedded thermal monitoring.
3.  **Project Handover**: Serving as the final submission for the B.Tech degree requirements.

### Important Note for Gemini CLI
The `.docx` file has been programmatically enhanced to include:
-   **Captions**: All figures (Fig 2.1 to Fig 4.5c) have clear, descriptive labels.
-   **Appendix**: A dedicated section for consolidated lists of figures and tables.
-   **Table of Contents**: A deep, multi-level TOC (up to `x.xx.xx`) reflecting the complete document hierarchy.
