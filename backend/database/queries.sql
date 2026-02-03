-- ARQUIVO DE CONSULTAS ANALÍTICAS
-- Este arquivo contém as queries SQL para extração de insights dos dados carregados.

-- 1. QUAIS AS 10 OPERADORAS QUE MAIS GASTARAM NO ÚLTIMO ANO?
-- Objetivo: Identificar os maiores players em volume de despesas.
SELECT 
    o.razao_social,
    o.registro_ans,
    SUM(d.valor_despesa) as total_despesas
FROM despesas_detalhadas d
JOIN operadoras o ON d.registro_ans = o.registro_ans
WHERE d.ano = 2024  -- Ajuste o ano conforme os dados baixados (ex: 2024 ou 2025)
GROUP BY o.razao_social, o.registro_ans
ORDER BY total_despesas DESC
LIMIT 10;

-- 2. QUAL A VARIAÇÃO DE DESPESAS POR TRIMESTRE?
-- Objetivo: Entender a sazonalidade das despesas.
SELECT 
    ano,
    trimestre,
    SUM(valor_despesa) as total_trimestre,
    COUNT(*) as qtd_lancamentos
FROM despesas_detalhadas
GROUP BY ano, trimestre
ORDER BY ano DESC, trimestre DESC;

-- 3. MÉDIA DE DESPESAS POR ESTADO (UF)
-- Objetivo: Comparar o custo médio das operadoras geograficamente.
-- Nota: Utiliza a tabela 'despesas_agregadas' criada para performance.
SELECT 
    uf,
    COUNT(razao_social) as qtd_operadoras,
    ROUND(AVG(total_despesas), 2) as media_despesa_por_operadora,
    SUM(total_despesas) as total_estado
FROM despesas_agregadas
WHERE uf IS NOT NULL
GROUP BY uf
ORDER BY total_estado DESC;

-- 4. OPERADORAS COM MAIOR INSTABILIDADE DE GASTOS (DESVIO PADRÃO)
-- Objetivo: Encontrar operadoras onde o gasto oscila muito entre trimestres.
SELECT 
    razao_social,
    uf,
    media_trimestral,
    desvio_padrao
FROM despesas_agregadas
WHERE desvio_padrao > 0
ORDER BY desvio_padrao DESC
LIMIT 10;