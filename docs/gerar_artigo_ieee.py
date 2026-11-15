"""Gera o artigo científico experimental completo no formato padrão IEEE Conference (2 colunas),
em formato .docx e converte automaticamente para .pdf via Word.
"""
from __future__ import annotations

import os
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(r"C:\Users\w4tts\Desktop\alertaedu")
DOCX_OUT = ROOT / "docs" / "Artigo_IEEE_AlertaEdu.docx"
PDF_OUT = ROOT / "docs" / "Artigo_IEEE_AlertaEdu.pdf"
FIG_DIR = ROOT / "reports" / "figures"

FONT_MAIN = "Times New Roman"
BLACK = RGBColor(0, 0, 0)
GRAY = RGBColor(80, 80, 80)


def set_run_font(run, name=FONT_MAIN, size=10, bold=False, italic=False, color=BLACK):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def add_p(container, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.05):
    p = container.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        set_run_font(r, size=10)
    return p


def add_sec_break(doc, num_cols=2, space_pts=14.4):
    """Cria uma quebra de seção contínua com número de colunas especificado."""
    new_sec = doc.add_section()
    sectPr = new_sec._sectPr
    # Continuous section break
    type_elem = OxmlElement("w:type")
    type_elem.set(qn("w:val"), "continuous")
    sectPr.append(type_elem)
    # Margins A4/Letter padrão IEEE (0.75 top, 1.0 bottom, 0.625 left/right)
    new_sec.top_margin = Inches(0.75)
    new_sec.bottom_margin = Inches(1.0)
    new_sec.left_margin = Inches(0.625)
    new_sec.right_margin = Inches(0.625)
    # Columns
    cols = OxmlElement("w:cols")
    cols.set(qn("w:num"), str(num_cols))
    cols.set(qn("w:space"), str(int(space_pts * 20)))  # in twips
    sectPr.append(cols)
    return new_sec


def add_heading_ieee(doc, num_roman, title):
    p = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)
    r = p.add_run(f"{num_roman}.  {title.upper()}")
    set_run_font(r, size=10, bold=True)
    return p


def add_subheading_ieee(doc, letter, title):
    p = add_p(doc, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2)
    r = p.add_run(f"{letter}.  {title}")
    set_run_font(r, size=10, italic=True, bold=False)
    return p


def set_cell_borders(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for b in ["top", "bottom"]:
        node = OxmlElement(f"w:{b}")
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "4")
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), "000000")
        tcBorders.append(node)
    for b in ["left", "right"]:
        node = OxmlElement(f"w:{b}")
        node.set(qn("w:val"), "none")
        tcBorders.append(node)
    tcPr.append(tcBorders)


def add_ieee_table(doc, caption, headers, rows):
    cp = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=3)
    r = cp.add_run(caption.upper())
    set_run_font(r, size=8.5, bold=True)

    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = "Table Grid"

    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h)
        set_run_font(r, size=8, bold=True)
        set_cell_borders(cell)

    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j <= 1 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            r = p.add_run(str(val))
            set_run_font(r, size=8)
            set_cell_borders(cell)
    add_p(doc, space_after=4)


def add_ieee_figure(doc, img_path, caption):
    if not img_path.exists():
        return
    p_img = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    p_img.add_run().add_picture(str(img_path), width=Inches(3.3))
    p_cap = add_p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=6)
    r1 = p_cap.add_run("Fig. ")
    set_run_font(r1, size=8.5, bold=True)
    r2 = p_cap.add_run(caption)
    set_run_font(r2, size=8.5)


def build_paper():
    doc = Document()

    # 1. Seção 1 (1 Coluna) - Título, Autores, Filiação
    s1 = doc.sections[0]
    s1.top_margin = Inches(0.75)
    s1.bottom_margin = Inches(1.0)
    s1.left_margin = Inches(0.625)
    s1.right_margin = Inches(0.625)

    # Título do Artigo
    p_title = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)
    r_t = p_title.add_run(
        "AlertaEdu: Estudo Experimental Comparativo de Machine Learning e Redes Neurais Artificiais para Previsão Precoce de Evasão no Ensino Superior"
    )
    set_run_font(r_t, size=24, bold=True)

    # Autores e Instituição
    p_auth = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=3)
    r_a = p_auth.add_run(
        "José Henrique, Ryan Budin, João Pedro Marques, Daniel Augusto, Matheus Miranda, Guilherme Polotto"
    )
    set_run_font(r_a, size=11, bold=True)

    p_aff = add_p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=14)
    r_aff = p_aff.add_run(
        "Departamento de Engenharia / Computação — Disciplina de Inteligência Artificial\n"
        "Projeto Experimental Integrado — Avaliação P2"
    )
    set_run_font(r_aff, size=10, italic=True)

    # 2. Seção 2 (2 Colunas) - Resumo, Abstract, Seções I a IX
    add_sec_break(doc, num_cols=2, space_pts=14.4)

    # Resumo
    p_res = add_p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=5)
    r_rb = p_res.add_run("Resumo— ")
    set_run_font(r_rb, size=9, bold=True, italic=True)
    r_rt = p_res.add_run(
        "A evasão acadêmica no ensino superior configura-se como um problema crônico de elevado impacto socioeconômico e institucional. "
        "Frequentemente, as intervenções de permanência estudantil falham por ocorrerem de forma tardia. "
        "Este trabalho apresenta um estudo experimental rigoroso para predição antecipada do risco de evasão universitária a partir do "
        "dataset público benchmark da UCI (4.424 estudantes e 36 atributos). Foram concebidos três cenários de antecedência operacional: "
        "(A) no ato da matrícula, (B) ao término do primeiro semestre e (C) ao término do segundo semestre. "
        "Realizou-se a comparação experimental entre quatro abordagens de Machine Learning e Redes Neurais: Regressão Logística regularizada, "
        "Random Forest, Extreme Gradient Boosting (XGBoost) e Rede Neural Artificial do tipo Perceptron Multicamadas (MLP). "
        "Sob validação cruzada estratificada em 5 partições e calibração de limiar ótimo orientado à métrica F2, o modelo XGBoost alcançou "
        "área sob a curva ROC (ROC-AUC) de 0,911 e Recall de 0,884 no fim do primeiro semestre, superando o baseline ingênuo (AUC 0,500). "
        "A Rede Neural Artificial MLP demonstrou acurácia de 87,2% e ROC-AUC de 0,914 no mesmo cenário, comprovando elevada capacidade de "
        "generalização em espaços não lineares. A explicabilidade foi assegurada pelo arcabouço SHAP (TreeSHAP), identificando o número de disciplinas "
        "aprovadas e o pagamento de mensalidades como os maiores preditores. Uma auditoria de justiça algorítmica revelou disparidades críticas de sensibilidade "
        "em estudantes bolsistas (Recall de 0,586 vs. 0,918 em não bolsistas), demonstrando a urgência de supervisão ética humana em sistemas de apoio à decisão."
    )
    set_run_font(r_rt, size=9)

    # Palavras-chave
    p_kw = add_p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=10)
    r_kb = p_kw.add_run("Palavras-chave— ")
    set_run_font(r_kb, size=9, bold=True, italic=True)
    r_kt = p_kw.add_run(
        "Evasão Universitária, Aprendizado de Máquina, Redes Neurais Artificiais, Multilayer Perceptron, XGBoost, Explicabilidade, SHAP, Auditoria de Justiça."
    )
    set_run_font(r_kt, size=9)

    # I. INTRODUÇÃO
    add_heading_ieee(doc, "I", "Introdução")
    add_p(
        doc,
        "A evasão no ensino superior representa uma das mais graves ineficiências educacionais contemporâneas. De acordo com dados do Instituto "
        "Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP, 2023–2024), a taxa média anual de desistência em cursos de graduação no Brasil "
        "atinge expressivos 17,5%, acarretando desperdício de recursos orçamentários públicos, perdas expressivas de mensalidades no setor privado e "
        "frustração de trajetórias humanas e profissionais."
    )
    add_p(
        doc,
        "O núcleo do problema reside na assimetria temporal da percepção institucional: quando o estudante tranca a matrícula ou abandona fisicamente "
        "as salas de aula, os mecanismos de apoio pedagógico e psicossocial tornam-se ineficazes. Não obstante, os sistemas acadêmicos armazenam continuamente "
        "dados de admissão, características sociodemográficas, histórico financeiro e desempenho nas disciplinas iniciais. Transformar esses registros brutos "
        "em sinais antecipados e acionáveis constitui o foco deste trabalho."
    )
    add_p(
        doc,
        "Neste contexto, o presente artigo formaliza e avalia experimentalmente o sistema AlertaEdu, concebido como um artefato de apoio à decisão "
        "que estima a probabilidade de evasão, classifica o nível de risco e decompõe as causas da previsão por meio de técnicas de Inteligência Artificial Explicável (XAI). "
        "O trabalho introduz uma formulação orientada a cenários operacionais de antecedência temporal, investigando o trade-off entre o momento do alerta e sua precisão."
    )

    # II. TRABALHOS RELACIONADOS E FUNDAMENTAÇÃO TEÓRICA
    add_heading_ieee(doc, "II", "Trabalhos Relacionados e Fundamentação")
    add_p(
        doc,
        "A predição de evasão discente mediante mineração de dados educacionais (Educational Data Mining - EDM) consolidou-se na literatura através de "
        "diversas famílias algorítmicas. Realinho et al. [1] compilaram o conjunto benchmark do Instituto Politécnico de Portalegre e avaliaram algoritmos "
        "tradicionais em formulação multiclasse (Dropout, Enrolled, Graduate), destacando a relevância dos fatores socioeconômicos e notas semestrais."
    )
    add_p(
        doc,
        "No domínio de dados tabulares estruturados, estudos seminais como o de Grinsztajn, Oyallon e Varoquaux [2] demonstraram que conjuntos de árvores "
        "de decisão baseadas em boosting, em particular o XGBoost [3], frequentemente superam arquiteturas de Deep Learning devido à sua invariância a transformações "
        "monotônicas e facilidade de manipulação de distribuições assimétricas. Paralelamente, redes neurais do tipo Multilayer Perceptron (MLP) com ativação ReLU e "
        "regularização adequada oferecem fronteiras de decisão contínuas altamente expressivas, sendo amplamente exploradas em tarefas de classificação acadêmica."
    )
    add_p(
        doc,
        "Um gargalo persistente na adoção dessas tecnologias reside na opacidade preditiva ('caixa-preta'). Para mitigar essa restrição, o método SHAP "
        "(SHapley Additive exPlanations), formalizado por Lundberg e Lee [4], fundamenta-se na teoria dos jogos cooperativos para atribuir a contribuição marginal exata "
        "de cada atributo. Por fim, a literatura recente de justiça algorítmica, sumarizada por Barocas et al. [5], enfatiza que métricas globais de acurácia ocultam "
        "vieses severos entre subgrupos vulneráveis, impondo auditorias desagregadas de sensibilidade e paridade de taxa de erros."
    )

    # III. METODOLOGIA
    add_heading_ieee(doc, "III", "Metodologia Experimental")
    add_subheading_ieee(doc, "A", "Base de Dados e Definição da Variável-Alvo")
    add_p(
        doc,
        "Utilizou-se o dataset benchmark 'Predict Students' Dropout and Academic Success' [1], hospedado no repositório UCI sob licença CC BY 4.0. "
        "A base é composta por 4.424 instâncias discentes individuais e 36 atributos de entrada. Os dados encontram-se integralmente consolidados, sem registros nulos "
        "ou duplicatas. A variável-alvo original (Target) possui distribuição: Graduate (49,9%), Dropout (32,1%) e Enrolled (17,9%). "
        "Para focar na priorização de intervenção preventiva, mapeou-se o problema como classificação binária: Evasão = 1 (Dropout, N=1.421) e Não-Evasão = 0 (Graduate ou Enrolled, N=3.003)."
    )

    add_subheading_ieee(doc, "B", "Cenários de Antecedência Operacional")
    add_p(
        doc,
        "A fim de evitar vazamento de dados futuros (data leakage) e avaliar a utilidade operacional do sistema ao longo do tempo, conceberam-se três cenários:"
    )
    add_p(
        doc,
        "1) Cenário A (No ato da matrícula): Utiliza 24 atributos sociodemográficos, qualificações anteriores e dados macroeconômicos. Não incorpora nenhuma avaliação curricular universitária.\n"
        "2) Cenário B (Fim do 1º Semestre): Incorpora 30 atributos, somando aos dados do Cenário A o desempenho em unidades curriculares do primeiro semestre (inscritas, avaliadas, aprovadas e notas).\n"
        "3) Cenário C (Fim do 2º Semestre): Totalidade dos 36 atributos, agregando todo o primeiro ano letivo discente."
    )

    add_subheading_ieee(doc, "C", "Protocolo de Particionamento e Validação")
    add_p(
        doc,
        "A base total foi particionada em conjunto de treino (80%, N=3.539) e conjunto de teste independente (20%, N=885), com estratificação pela classe minoritária "
        "e fixação da semente pseudoaleatória (seed=42). Toda a seleção de hiperparâmetros e estimativa de variância foi conduzida exclusivamente no conjunto de treino "
        "mediante Validação Cruzada Estratificada de 5 partições (5-fold Stratified CV). O conjunto de teste permaneceu intacto até a avaliação confirmatória."
    )

    # IV. CONFIGURAÇÃO EXPERIMENTAL E MODELOS
    add_heading_ieee(doc, "IV", "Modelos e Configuração Experimental")
    add_p(
        doc,
        "Para responder à exigência de comparação sistemática de técnicas, foram implementados e comparados quatro métodos no mesmo pipeline scikit-learn:"
    )
    add_p(
        doc,
        "1) Baseline (Ingênuo): Classificador que prevê estritamente a classe majoritária (Zero-R), servindo como piso de referência.\n"
        "2) Regressão Logística (LR): Modelo linear regularizado L2 com ponderação balanceada de classes (class_weight='balanced') e One-Hot Encoding com truncamento de frequência para atributos nominais.\n"
        "3) Random Forest (RF): Ensemble de 400 árvores de decisão, com amostragem balanceada em subsample e profundidade irrestrita com folhas mínimas de 3 amostras.\n"
        "4) Extreme Gradient Boosting (XGBoost): Ensemble de 300 árvores aditivas com taxa de aprendizado 0,05, subamostragem de linhas e colunas de 80%, e ponderação scale_pos_weight calibrada para desbalanceamento.\n"
        "5) Rede Neural Artificial (MLP): Perceptron Multicamadas composto por duas camadas ocultas de 64 e 32 neurônios, função de ativação ReLU, otimizador Adam, early stopping (paciência de 10 épocas) e normalização StandardScaler das variáveis numéricas contínuas."
    )

    add_subheading_ieee(doc, "A", "Métricas e Otimização do Limiar de Decisão (F2)")
    add_p(
        doc,
        "A avaliação adotou Acurácia, Precisão, Sensibilidade (Recall), F1-Score e Área sob a Curva ROC (ROC-AUC). Em aplicações de permanência estudantil, o custo de um Falso Negativo "
        "(deixar de identificar um aluno que evadirá) supera expressivamente o custo de um Falso Positivo (oferecer tutoria preventiva a quem não precisaria). "
        "Dessa forma, otimizou-se o limiar de corte de probabilidade nas predições out-of-fold do treino utilizando a métrica F2 (peso dobrado para o Recall):"
    )
    add_p(
        doc,
        "F_beta = (1 + beta^2) * (Precisao * Recall) / (beta^2 * Precisao + Recall), onde beta = 2.",
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    # V. RESULTADOS EXPERIMENTAIS
    add_heading_ieee(doc, "V", "Resultados Experimentais")
    add_p(
        doc,
        "A Tabela I sumariza o desempenho comparativo de todos os modelos nos três cenários de antecedência avaliados no conjunto de teste independente (N=885)."
    )

    # Tabela I
    tab1_headers = [
        "Cenário",
        "Modelo",
        "CV-F1",
        "Acurácia",
        "Precisão",
        "Recall",
        "F1-Score",
        "ROC-AUC",
    ]
    tab1_rows = [
        ["A (Matrícula)", "Baseline", "0,000", "0,679", "0,000", "0,000", "0,000", "0,500"],
        ["A (Matrícula)", "Reg. Logística", "0,646", "0,756", "0,601", "0,715", "0,653", "0,838"],
        ["A (Matrícula)", "Random Forest", "0,623", "0,793", "0,710", "0,602", "0,651", "0,825"],
        ["A (Matrícula)", "XGBoost", "0,639", "0,771", "0,629", "0,697", "0,661", "0,835"],
        ["A (Matrícula)", "Rede Neural (MLP)", "0,607", "0,800", "0,751", "0,563", "0,644", "0,839"],
        ["B (1º Sem.)", "Baseline", "0,000", "0,679", "0,000", "0,000", "0,000", "0,500"],
        ["B (1º Sem.)", "Reg. Logística", "0,761", "0,858", "0,762", "0,810", "0,785", "0,914"],
        ["B (1º Sem.)", "Random Forest", "0,756", "0,859", "0,805", "0,739", "0,771", "0,908"],
        ["B (1º Sem.)", "XGBoost", "0,763", "0,861", "0,773", "0,803", "0,788", "0,911"],
        ["B (1º Sem.)", "Rede Neural (MLP)", "0,754", "0,872", "0,825", "0,764", "0,793", "0,914"],
        ["C (2º Sem.)", "Baseline", "0,000", "0,679", "0,000", "0,000", "0,000", "0,500"],
        ["C (2º Sem.)", "Reg. Logística", "0,787", "0,884", "0,803", "0,845", "0,823", "0,932"],
        ["C (2º Sem.)", "Random Forest", "0,787", "0,881", "0,840", "0,778", "0,808", "0,932"],
        ["C (2º Sem.)", "XGBoost", "0,792", "0,885", "0,820", "0,820", "0,820", "0,934"],
        ["C (2º Sem.)", "Rede Neural (MLP)", "0,794", "0,885", "0,879", "0,743", "0,805", "0,936"],
    ]
    add_ieee_table(
        doc,
        "Tabela I: Desempenho Comparativo Experimental nos Três Cenários de Alerta (Conjunto de Teste, N=885)",
        tab1_headers,
        tab1_rows,
    )

    add_p(
        doc,
        "A análise dos dados evidencia uma progressão monotônica consistente de capacidade preditiva: no Cenário A, a melhor ROC-AUC atinge 0,839 (MLP); "
        "com a inclusão do 1º semestre (Cenário B), salta para 0,914 (MLP e Regressão Logística) e 0,911 (XGBoost); atingindo 0,936 no Cenário C. "
        "A Rede Neural Artificial MLP obteve a mais elevada Acurácia (87,2% no Cenário B e 88,5% no Cenário C) e alta Precisão (82,5% e 87,9%), "
        "enquanto o XGBoost e a Regressão Logística apresentaram maior Sensibilidade nativa."
    )

    # Figura ROC
    add_ieee_figure(
        doc,
        FIG_DIR / "roc_B_1_semestre.png",
        "Curvas ROC comparativas para os modelos preditivos no Cenário B (Fim do 1º Semestre, Teste N=885).",
    )

    add_subheading_ieee(doc, "A", "Impacto da Calibração do Limiar F2")
    add_p(
        doc,
        "Ao aplicar o limiar ótimo F2 no modelo implantado (XGBoost), os resultados operacionais foram transformados: no Cenário A (limiar=0,23), "
        "o Recall elevou-se para 0,919 (Precisão=0,436); no Cenário B (limiar=0,25), o Recall atingiu 0,884 (Precisão=0,584); e no Cenário C (limiar=0,18), "
        "o Recall alcançou 0,937 (Precisão=0,576). A Fig. 2 ilustra a matriz de confusão resultante no Cenário B."
    )

    # Figura Matriz de Confusão
    add_ieee_figure(
        doc,
        FIG_DIR / "confusao_B_1_semestre.png",
        "Matriz de confusão do modelo XGBoost calibrado com limiar F2=0,25 no Cenário B.",
    )

    # VI. EXPLICABILIDADE E AUDITORIA DE JUSTIÇA
    add_heading_ieee(doc, "VI", "Explicabilidade e Auditoria de Justiça")
    add_subheading_ieee(doc, "A", "Importância Global e Local via TreeSHAP")
    add_p(
        doc,
        "A aplicação do TreeSHAP revelou que o atributo mais determinante para o risco de evasão no primeiro ano é o número de disciplinas aprovadas "
        "no 1º semestre (importância média SHAP de 1,190), seguido da pontualidade no pagamento de mensalidades (0,470), da média de notas (0,354) e "
        "da idade no momento da matrícula (0,336). A Fig. 3 apresenta a distribuição das contribuições SHAP."
    )

    # Figura SHAP
    add_ieee_figure(
        doc,
        FIG_DIR / "shap_summary_B_1_semestre.png",
        "Valores SHAP para os 15 principais atributos preditivos no Cenário B (Fim do 1º Semestre).",
    )

    add_subheading_ieee(doc, "B", "Auditoria Experimental de Justiça Algorítmica")
    add_p(
        doc,
        "Para avaliar os potenciais impactos éticos do classificador, foi realizada uma auditoria por subgrupos no conjunto de teste do Cenário B "
        "(limiar calibrado=0,25). A Tabela II apresenta as taxas empíricas de alerta, sensibilidade e falsos positivos."
    )

    # Tabela II
    tab2_headers = [
        "Atributo",
        "Subgrupo",
        "Amostras (N)",
        "Taxa Real",
        "Taxa Alerta",
        "Recall",
        "Falso Positivo",
    ]
    tab2_rows = [
        ["Gênero", "Feminino", "564", "24,5%", "39,2%", "0,870", "23,7%"],
        ["Gênero", "Masculino", "321", "45,5%", "65,1%", "0,897", "44,6%"],
        ["Bolsa", "Não Bolsista", "654", "39,0%", "58,0%", "0,918", "36,3%"],
        ["Bolsa", "Bolsista", "231", "12,6%", "22,1%", "0,586", "16,8%"],
        ["Dívida", "Não Devedor", "795", "29,2%", "44,8%", "0,858", "27,9%"],
        ["Dívida", "Devedor", "90", "57,8%", "82,2%", "1,000", "57,9%"],
    ]
    add_ieee_table(
        doc,
        "Tabela II: Auditoria de Justiça Algorítmica por Subgrupos Vulneráveis (Cenário B, Teste N=885)",
        tab2_headers,
        tab2_rows,
    )

    # VII. DISCUSSÃO
    add_heading_ieee(doc, "VII", "Discussão dos Resultados")
    add_p(
        doc,
        "Os achados experimentais revelam três contribuições centrais para o campo de Educational Data Mining:\n"
        "1) Janela Ótima de Intervenção: O Cenário A (matrícula) apresenta elevada taxa de falsos positivos (precisão de 43,6%), inviabilizando "
        "intervenções massivas pelo custo de saturação das equipes. Já o Cenário B (fim do 1º semestre) alcança ROC-AUC de 0,911 e capta 88,4% das evasões "
        "com antecedência temporal suficiente para retenção no segundo semestre, estabelecendo-se como a janela operacional ideal.\n"
        "2) Equilíbrio entre Complexidade e Desempenho: Observou-se que a Rede Neural MLP alcançou excelente acurácia e precisão, e a Regressão Logística "
        "obteve AUC comparável ao XGBoost. Contudo, modelos baseados em árvores viabilizam cálculo exato de atribuição local via TreeSHAP com custo O(TLD^2), "
        "enquanto métodos agnósticos para redes neurais (como KernelSHAP) impõem aproximações estocásticas computacionalmente proibitivas em produção.\n"
        "3) Disparidade Crítica em Bolsistas: A auditoria algorítmica revelou uma vulnerabilidade de justiça expressiva: o modelo falha em capturar mais de 41% "
        "dos bolsistas em risco (Recall=0,586), contra apenas 8,2% em não bolsistas. Isso decorre da reduzida taxa basal de evasão desse grupo (12,6%). "
        "Consequentemente, sistemas de IA pedagógica exigem calibrações de limiares específicas por grupo ou pós-processamento de equalização de oportunidades."
    )

    # VIII. CONCLUSÃO
    add_heading_ieee(doc, "VIII", "Conclusão e Trabalhos Futuros")
    add_p(
        doc,
        "Este trabalho desenvolveu e avaliou criticamente uma solução funcional para identificação precoce de evasão discente no ensino superior. "
        "Comprovou-se empiricamente que o encerramento do primeiro semestre curricular fornece o compromisso ideal entre antecedência de intervenção e "
        "confiabilidade estatística (ROC-AUC 0,911 e Recall 0,884). A incorporação da Rede Neural Artificial MLP demonstrou a viabilidade de modelagem "
        "não linear com precisão de 82,5%, complementando o XGBoost.\n"
        "Como trabalhos futuros, propõe-se: (i) treinamento com microdados brasileiros do Censo Superior (INEP), (ii) aplicação de restrições de paridade demográfica "
        "para mitigação de viés em bolsistas, e (iii) formulação de análise de sobrevivência para predizer o tempo exato até o abandono."
    )

    # DECLARAÇÃO DE USO DE IA
    p_ia_h = add_p(
        doc, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=2
    )
    r_iah = p_ia_h.add_run("Declaração de Uso de Inteligência Artificial")
    set_run_font(r_iah, size=9.5, bold=True)
    add_p(
        doc,
        "Durante a concepção deste artigo e de seus artefatos, utilizou-se o modelo de linguagem Antigravity (Google DeepMind) como copiloto de pesquisa, "
        "auxiliando na estruturação do código experimental Python, automatização de pipelines gráficos, formatação das tabelas e revisão estilística. "
        "Todos os experimentos foram executados e validados localmente pela equipe com sementes fixadas, sendo os autores integralmente responsáveis "
        "pelas análises, conclusões e integridade técnica aqui apresentadas.",
        space_after=6,
    )

    # REFERÊNCIAS
    add_heading_ieee(doc, "IX", "Referências")
    refs = [
        "[1] V. Realinho, J. Machado, L. Baptista, and M. V. Martins, \"Predicting student dropout and academic success,\" Data, vol. 7, no. 11, art. 146, 2022. doi: 10.3390/data7110146.",
        "[2] L. Grinsztajn, E. Oyallon, and G. Varoquaux, \"Why do tree-based models still outperform deep learning on typical tabular data?\" in Advances in Neural Information Processing Systems (NeurIPS), 2022.",
        "[3] T. Chen and C. Guestrin, \"XGBoost: A scalable tree boosting system,\" in Proc. 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining, 2016, pp. 785–794.",
        "[4] S. M. Lundberg and S.-I. Lee, \"A unified approach to interpreting model predictions,\" in Advances in Neural Information Processing Systems (NeurIPS), 2017, pp. 4765–4774.",
        "[5] S. Barocas, M. Hardt, and A. Narayanan, Fairness and Machine Learning: Limitations and Opportunities. Cambridge, MA: MIT Press, 2023.",
        "[6] F. Pedregosa et al., \"Scikit-learn: Machine learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
        "[7] L. Breiman, \"Random forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
        "[8] S. M. Lundberg et al., \"From local explanations to global understanding with explainable AI for trees,\" Nature Machine Intelligence, vol. 2, pp. 56–67, 2020.",
        "[9] INEP, \"Censo da Educação Superior: Indicadores de Fluxo da Educação Superior,\" Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira, Brasília, DF, 2024.",
        "[10] Brasil, \"Lei nº 13.709, de 14 de agosto de 2018 (Lei Geral de Proteção de Dados Pessoais - LGPD),\" Diário Oficial da União, Brasília, DF, 2018.",
    ]
    for r in refs:
        p_ref = add_p(
            doc,
            r,
            align=WD_ALIGN_PARAGRAPH.JUSTIFY,
            space_before=1,
            space_after=2,
            line_spacing=1.0,
        )
        for run in p_ref.runs:
            set_run_font(run, size=8)

    doc.save(DOCX_OUT)
    print("Artigo Word IEEE gerado com sucesso:", DOCX_OUT)


if __name__ == "__main__":
    build_paper()
