# 🚀 Student Guide: Vivado Design Flows (UG888)

Welcome! If you are new to FPGA design, **UG888** is your roadmap. It explains how to take your ideas (code) and turn them into reality (hardware) using Xilinx's **Vivado** software.

---

## 1. The Big Idea: Two Ways to Work
Vivado gives you two "modes." Think of it like cooking:

### 🏠 Project Mode (The "Chef's Kitchen")
*   **What it is:** The software manages everything for you. It creates folders, tracks your files, and remembers your settings.
*   **Best for:** Students and most professional designs.
*   **Key Feature:** The **Flow Navigator** (a simple sidebar that guides you from step 1 to step 10).
*   **Analogy:** Like using a smart oven where you just press "Bake" and it handles the temperature and timing.

### 📜 Non-Project Mode (The "Outdoor Campfire")
*   **What it is:** You do everything manually using **Tcl scripts** (text commands). There is no "project file." Everything happens in the computer's memory.
*   **Best for:** Experts who want to automate everything or run designs on a server without a screen.
*   **Key Feature:** You use **Checkpoints (.dcp)** to save your work manually.
*   **Analogy:** Like building a fire from scratch. It's harder, but you have total control over every spark.

---

## 2. The "Life Cycle" of a Design
Regardless of the mode, every design goes through these 5 phases:

1.  **Design Entry:** You write your logic in **Verilog** or **VHDL** and add your **Constraints** (which tell the chip which pins to use).
2.  **Synthesis:** Vivado reads your code and turns it into a "Netlist" (a giant map of basic logic gates).
3.  **Implementation:**
    *   **Placement:** Vivado finds the best physical spot on the chip for each gate.
    *   **Routing:** Vivado connects those spots with physical wires inside the chip.
4.  **Verification:** You look at reports to make sure your signals aren't "too slow" (Timing Analysis).
5.  **Bitstream:** Vivado creates a `.bit` file—this is the actual data you "upload" to the FPGA.

---

## 3. What You Learn in the Labs

### 🧪 Lab 1: The Scripting Flow
In this lab, you don't click buttons. You run a command that says `source run.tcl`. 
*   **The Goal:** See how Vivado works "under the hood."
*   **Key Skill:** Learning how to open a completed design in the GUI even if you didn't use Project Mode.

### 🧪 Lab 2: The GUI Flow
This is where most students spend their time.
*   **The Goal:** Use the "New Project Wizard" to set up a design.
*   **Key Skill:** Using the **IP Catalog**. This is like a "Store" where you can grab pre-made parts (like a math block or a memory controller) so you don't have to code them from scratch.

---

## 🌟 Pro-Tips for Students
*   **Watch the Tcl Console:** Every time you click a button in the GUI, Vivado prints a text command in the bottom window. If you want to learn how to script, watch that window!
*   **Checkpoints are Life:** In professional work, `.dcp` files are your "Save Games." You can open them at any time to see exactly what your design looked like after Synthesis or Implementation.
*   **The "Flow Navigator" is your Friend:** If you get lost, just look at the sidebar on the left. It lists the steps in the exact order you should perform them.
