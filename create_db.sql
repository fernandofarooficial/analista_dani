-- ============================================================
-- DaniApp – Script de criação do banco de dados
-- Execute no DBeaver conectado ao servidor PostgreSQL
-- ============================================================

-- 1. Criar o banco de dados (execute conectado ao banco 'lojas' ou 'postgres')
-- CREATE DATABASE daniapp
--     OWNER = fefa_dev
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'pt_BR.UTF-8'
--     LC_CTYPE = 'pt_BR.UTF-8'
--     CONNECTION LIMIT = -1;

-- 2. Depois conecte ao banco 'daniapp' e execute o restante:

SET TIME ZONE 'America/Sao_Paulo';

-- ============================================================
-- Tabela: pacientes
-- ============================================================
CREATE TABLE IF NOT EXISTS pacientes (
    id               SERIAL PRIMARY KEY,
    nome_completo    VARCHAR(200) NOT NULL,
    nome             VARCHAR(100),
    cpf              VARCHAR(14) UNIQUE,
    rg               VARCHAR(20),
    email            VARCHAR(200),
    telefone         VARCHAR(20),
    endereco         VARCHAR(200),
    numero           VARCHAR(10),
    complemento      VARCHAR(100),
    bairro           VARCHAR(100),
    cidade           VARCHAR(100),
    estado           VARCHAR(2),
    cep              VARCHAR(9),
    data_nascimento  DATE,
    escolaridade     VARCHAR(60),
    genero           VARCHAR(30),
    estado_civil     VARCHAR(30),
    profissao        VARCHAR(100),
    naturalidade     VARCHAR(100),
    envia_parabens   BOOLEAN NOT NULL DEFAULT TRUE,
    ativo            BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE pacientes IS 'Cadastro de pacientes da psicanalista';
COMMENT ON COLUMN pacientes.envia_parabens IS 'Se TRUE envia WhatsApp de aniversário; se FALSE apenas alerta a psicanalista';

-- ============================================================
-- Tabela: anamneses
-- ============================================================
CREATE TABLE IF NOT EXISTS anamneses (
    id                           SERIAL PRIMARY KEY,
    paciente_id                  INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,

    -- Seção 1 – Dados Cadastrais Complementares
    indicacao                    VARCHAR(200),
    fuma                         VARCHAR(50),
    bebe                         VARCHAR(50),
    drogas                       VARCHAR(50),
    vicios_compulsoes            TEXT,
    fez_terapia_anterior         TEXT,

    -- Seção 2 – Configuração Familiar
    conjuge                      VARCHAR(200),
    mae                          VARCHAR(200),
    pai                          VARCHAR(200),
    irmaos                       TEXT,
    ordem_filho                  VARCHAR(50),
    filhos                       TEXT,

    -- Seção 3 – Dados Sigilosos
    queixa_principal             TEXT,
    historico_queixa_atual       TEXT,
    hist_infancia                TEXT,
    hist_adolescencia            TEXT,
    hist_vida_adulta             TEXT,
    hist_dinamica_familiar       TEXT,
    saude_medicacoes             TEXT,
    saude_tratamentos_anteriores TEXT,
    saude_sono_alimentacao       TEXT,

    -- Seção 4 – Impressões do Analista
    aparencia_atitude            TEXT,
    hipotese_diagnostica         TEXT,
    contratransferencia          TEXT,
    prognostico_plano            TEXT,

    created_at                   TIMESTAMP DEFAULT NOW(),
    updated_at                   TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE anamneses IS 'Ficha de Anamnese Psicanalítica – um paciente pode ter múltiplas fichas';

-- ============================================================
-- Tabela: notas_paciente
-- ============================================================
CREATE TABLE IF NOT EXISTS notas_paciente (
    id           SERIAL PRIMARY KEY,
    paciente_id  INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    texto        TEXT NOT NULL,
    created_at   TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE notas_paciente IS 'Notas livres da psicanalista sobre cada paciente';

-- ============================================================
-- Tabela: agendamentos
-- ============================================================
CREATE TABLE IF NOT EXISTS agendamentos (
    id               SERIAL PRIMARY KEY,
    paciente_id      INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    data_hora        TIMESTAMP NOT NULL,
    valor_consulta   NUMERIC(10,2) DEFAULT 0,
    valor_custo      NUMERIC(10,2) DEFAULT 0,
    confirmado       BOOLEAN NOT NULL DEFAULT FALSE,
    whatsapp_enviado BOOLEAN NOT NULL DEFAULT FALSE,
    observacoes      TEXT,
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW()
);

COMMENT ON COLUMN agendamentos.confirmado IS 'Marca que a sessão foi realizada (usado na contabilidade)';
COMMENT ON COLUMN agendamentos.valor_custo IS 'Valor de custo adicional referente a esta sessão específica';
COMMENT ON COLUMN agendamentos.whatsapp_enviado IS 'Controle para não reenviar o lembrete automático de 24h';

-- ============================================================
-- Tabela: configuracoes
-- ============================================================
CREATE TABLE IF NOT EXISTS configuracoes (
    id     SERIAL PRIMARY KEY,
    chave  VARCHAR(100) UNIQUE NOT NULL,
    valor  TEXT
);

COMMENT ON TABLE configuracoes IS 'Configurações gerais do app (valores padrão, WhatsApp, etc.)';

-- ============================================================
-- Dados iniciais – Configurações padrão
-- ============================================================
INSERT INTO configuracoes (chave, valor) VALUES
    ('valor_consulta',    '200.00'),
    ('valor_custo',       '0.00'),
    ('psicanal_nome',     'Dani'),
    ('psicanal_telefone', ''),
    ('whatsapp_api_url',  ''),
    ('whatsapp_api_key',  ''),
    ('whatsapp_instance', 'daniapp'),
    ('callmebot_phone',   ''),
    ('callmebot_api_key', '')
ON CONFLICT (chave) DO NOTHING;

-- ============================================================
-- Índices para melhor desempenho
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_pacientes_nome ON pacientes(nome_completo);
CREATE INDEX IF NOT EXISTS idx_pacientes_ativo ON pacientes(ativo);
CREATE INDEX IF NOT EXISTS idx_pacientes_nascimento ON pacientes(data_nascimento);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data ON agendamentos(data_hora);
CREATE INDEX IF NOT EXISTS idx_agendamentos_confirmado ON agendamentos(confirmado);
CREATE INDEX IF NOT EXISTS idx_agendamentos_paciente ON agendamentos(paciente_id);
CREATE INDEX IF NOT EXISTS idx_anamneses_paciente ON anamneses(paciente_id);
CREATE INDEX IF NOT EXISTS idx_notas_paciente ON notas_paciente(paciente_id);

-- ============================================================
-- Trigger para atualizar updated_at automaticamente
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_pacientes_updated
    BEFORE UPDATE ON pacientes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_anamneses_updated
    BEFORE UPDATE ON anamneses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_agendamentos_updated
    BEFORE UPDATE ON agendamentos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
