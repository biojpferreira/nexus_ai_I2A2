from tools import VRVAAutomationTools


vrva_tools_instance = VRVAAutomationTools()
FILES_PATH = {
    "ativos":"data/ATIVOS.xlsx",
    "ferias":"data/FÉRIAS.xlsx",
    "aprendiz":"data/APRENDIZ.xlsx",
    "admissao_abril":"data/ADMISSÃO ABRIL.xlsx",
    "ferias":"data/FÉRIAS.xlsx",
    "exterior":"data/EXTERIOR.xlsx",
    "estagio":"data/ESTÁGIO.xlsx",
    "desligados":"data/DESLIGADOS.xlsx",
    "afastamento":"data/AFASTAMENTOS.xlsx",
    "dias_uteis":"data/Base dias uteis.xlsx",
    "sindicato":"data/Base sindicato x valor.xlsx",
    "vr_mensal":"data/VR MENSAL 05.2025.xlsx"
}

print(vrva_tools_instance.read_xlsx(FILES_PATH['dias_uteis']))