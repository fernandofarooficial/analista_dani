from datetime import datetime
from app.extensions import db


class Paciente(db.Model):
    __tablename__ = 'pacientes'

    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100))
    cpf = db.Column(db.String(14), unique=True)
    rg = db.Column(db.String(20))
    email = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    cep = db.Column(db.String(9))
    data_nascimento = db.Column(db.Date)
    escolaridade = db.Column(db.String(60))
    genero = db.Column(db.String(30))
    estado_civil = db.Column(db.String(30))
    profissao = db.Column(db.String(100))
    naturalidade = db.Column(db.String(100))
    envia_parabens = db.Column(db.Boolean, default=True, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    anamneses = db.relationship('Anamnese', backref='paciente', lazy=True, cascade='all, delete-orphan')
    notas = db.relationship('NotaPaciente', backref='paciente', lazy=True, cascade='all, delete-orphan',
                            order_by='NotaPaciente.created_at.desc()')
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy=True, cascade='all, delete-orphan',
                                   order_by='Agendamento.data_hora.desc()')

    @property
    def nome_exibicao(self):
        return self.nome or self.nome_completo.split()[0]

    @property
    def telefone_whatsapp(self):
        if not self.telefone:
            return None
        digits = ''.join(c for c in self.telefone if c.isdigit())
        if not digits.startswith('55'):
            digits = '55' + digits
        return digits

    def __repr__(self):
        return f'<Paciente {self.nome_completo}>'


class Anamnese(db.Model):
    __tablename__ = 'anamneses'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    # Seção 1 – Dados Cadastrais (complementares ao cadastro)
    indicacao = db.Column(db.String(200))
    fuma = db.Column(db.String(50))
    bebe = db.Column(db.String(50))
    drogas = db.Column(db.String(50))
    vicios_compulsoes = db.Column(db.Text)
    fez_terapia_anterior = db.Column(db.Text)
    # Seção 2 – Configuração Familiar
    conjuge = db.Column(db.String(200))
    mae = db.Column(db.String(200))
    pai = db.Column(db.String(200))
    irmaos = db.Column(db.Text)
    ordem_filho = db.Column(db.String(50))
    filhos = db.Column(db.Text)
    # Seção 3 – Dados Sigilosos
    queixa_principal = db.Column(db.Text)
    historico_queixa_atual = db.Column(db.Text)
    hist_infancia = db.Column(db.Text)
    hist_adolescencia = db.Column(db.Text)
    hist_vida_adulta = db.Column(db.Text)
    hist_dinamica_familiar = db.Column(db.Text)
    saude_medicacoes = db.Column(db.Text)
    saude_tratamentos_anteriores = db.Column(db.Text)
    saude_sono_alimentacao = db.Column(db.Text)
    # Seção 4 – Impressões do Analista
    aparencia_atitude = db.Column(db.Text)
    hipotese_diagnostica = db.Column(db.Text)
    contratransferencia = db.Column(db.Text)
    prognostico_plano = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Anamnese {self.id} paciente={self.paciente_id}>'


class NotaPaciente(db.Model):
    __tablename__ = 'notas_paciente'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Nota {self.id}>'


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    valor_consulta = db.Column(db.Numeric(10, 2), default=0)
    valor_custo = db.Column(db.Numeric(10, 2), default=0)
    confirmado = db.Column(db.Boolean, default=False, nullable=False)
    whatsapp_enviado = db.Column(db.Boolean, default=False, nullable=False)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Agendamento {self.id} {self.data_hora}>'


class Configuracao(db.Model):
    __tablename__ = 'configuracoes'

    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text)

    @classmethod
    def get(cls, chave, default=None):
        cfg = cls.query.filter_by(chave=chave).first()
        return cfg.valor if cfg else default

    @classmethod
    def set(cls, chave, valor):
        cfg = cls.query.filter_by(chave=chave).first()
        if cfg:
            cfg.valor = str(valor) if valor is not None else ''
        else:
            cfg = cls(chave=chave, valor=str(valor) if valor is not None else '')
            db.session.add(cfg)
        db.session.commit()

    def __repr__(self):
        return f'<Configuracao {self.chave}={self.valor}>'
