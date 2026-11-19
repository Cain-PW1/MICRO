import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


@cocotb.test()
async def test_project(dut):
    dut._log.info("Inicio de la simulación")

    # Configurar reloj con periodo de 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # 1. Prueba de Reset (activo en bajo)
    dut._log.info("Probando Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await FallingEdge(dut.clk)
    assert int(dut.uo_out.value) == 0, f"Esperado 0 tras reset, obtenido {int(dut.uo_out.value)}"

    # 2. Prueba de Carga Paralela (OPR = 2'b11 -> uio_in = 3)
    dut._log.info("Probando Carga Paralela (DIN = 0b10100101)")
    dut.uio_in.value = 0b00000011  # OPR = 11 (Cargar DIN)
    dut.ui_in.value  = 0b10100101  # DIN = 165 (0xA5)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert int(dut.uo_out.value) == 0b10100101

    # 3. Prueba de Mantener (OPR = 2'b00 -> uio_in = 0)
    dut._log.info("Probando Mantener dato")
    dut.uio_in.value = 0b00000000  # OPR = 00 (Mantener)
    dut.ui_in.value  = 0b11111111  # Cambiamos DIN para verificar que no lo cargue
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert int(dut.uo_out.value) == 0b10100101

    # 4. Prueba de Desplazamiento a la Izquierda (OPR = 2'b01 -> uio_in = 1)
    dut._log.info("Probando Desplazamiento Izquierda")
    dut.uio_in.value = 0b00000001  # OPR = 01 (<< 1)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    # 0b10100101 << 1 = 0b01001010
    assert int(dut.uo_out.value) == 0b01001010

    # 5. Prueba de Desplazamiento a la Derecha (OPR = 2'b10 -> uio_in = 2)
    dut._log.info("Probando Desplazamiento Derecha")
    dut.uio_in.value = 0b00000010  # OPR = 10 (>> 1)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    # 0b01001010 >> 1 = 0b00100101
    assert int(dut.uo_out.value) == 0b00100101

    dut._log.info("¡Todas las pruebas pasaron correctamente!")
