from os import makedirs
from sqlalchemy import create_engine, func, desc, CheckConstraint, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError

makedirs("db",exist_ok=True)

engine = create_engine("sqlite:///db/app_db.db", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()



class Transacao(Base):
    __tablename__ = "transacoes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    Pessoa = Column(String(30), nullable=False)
    Tipo = Column(String, nullable=False)
    Categoria = Column(String, nullable=False)
    Descricao = Column(String(60), nullable=False)
    Local = Column(String, nullable=False)
    Valor = Column(Float, nullable=False)
    Moeda = Column(String, nullable=False)
    Cotacao = Column(Float, nullable=False)
    Valor_Total = Column(Float, nullable=False)
    Data = Column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint("Tipo IN ('Receita','Despesa')"),
        CheckConstraint("(Tipo = 'Receita' AND Categoria IN ('Salário', 'Rendimento', 'Outro')) "
                        "OR "
                        "(Tipo = 'Despesa' AND Categoria IN ('Alimentação', 'Transporte', 'Lazer', 'Saúde', 'Hospedagem', 'Passagem', 'Documento', 'Outro'))"),
        CheckConstraint("Local IN ('Brasil','Coreia','Japão','Outro')"),
        CheckConstraint("Valor > 0"),
        CheckConstraint("Moeda IN ('Real','Dolar','Won','Yen')"),
        CheckConstraint("(Cotacao > 0) AND ((Moeda != 'Real') OR (Cotacao = 1))"),
        CheckConstraint("Valor_Total > 0")
    )



def todas_transacoes(tipo=None, name="id", direct = "desc"):
    try:
        query = session.query(Transacao)

        if tipo:
            query = query.filter(Transacao.Tipo == tipo)

        coluna = getattr(Transacao, name)

        if isinstance(coluna.type, String):
            coluna = func.lower(coluna)        
        if direct == "desc":
            transacoes = query.order_by(desc(coluna)).all()
        elif direct == "asc":
            transacoes = query.order_by(coluna).all()


        dados = []
        for t in transacoes:
            dados.append({
                "id": t.id,
                "Pessoa": t.Pessoa,
                "Tipo": t.Tipo,
                "Categoria": t.Categoria,
                "Descricao": t.Descricao,
                "Local": t.Local,
                "Valor": t.Valor,
                "Moeda": t.Moeda,
                "Cotacao": t.Cotacao,
                "Valor_Total": t.Valor_Total,
                "Data": t.Data.date().strftime("%d/%m/%Y")
            })
        return dados
    except Exception as e:
        return f"Erro ao carregar transações: {e}"



def adicionar_transacao(form):
    transacao= Transacao(
                            Pessoa = form["Pessoa"],
                            Tipo = form["Tipo"],
                            Categoria = form["Categoria"],
                            Descricao = form["Descricao"].strip(),
                            Local = form["Local"],
                            Valor = float(form["Valor"]),
                            Moeda = form["Moeda"],
                            Cotacao = float(form["Cotacao"]),
                            Valor_Total = round(float(form["Valor"]) * float(form["Cotacao"]),2),
                            Data = form["Data"]
                        )

    try:
        session.add(transacao)
        session.commit()
        return "Transação adicionada com sucesso!"

    except IntegrityError as e:
        session.rollback() 
        return f"Erro ao adicionar transação: {e}"



def update_transacao(form):
    try:

        t = session.query(Transacao).filter(Transacao.id == form["Id"]).first()
        
        if t:
            t.Pessoa = form["Pessoa"]
            t.Tipo = form["Tipo"]
            t.Categoria = form["Categoria"]
            t.Descricao = form["Descricao"].strip()
            t.Local = form["Local"]
            t.Valor = float(form["Valor"])
            t.Moeda = form["Moeda"]
            t.Cotacao = float(form["Cotacao"])
            t.Valor_Total = round(float(form["Valor"]) * float(form["Cotacao"]),2)
            t.Data = form["Data"]
            session.commit()
            return "Transação atualizada com sucesso!"
        
        return "Transação não encontrada."
    
    except Exception as e:
    
        session.rollback()
        return f"Erro ao atualizar: {e}"
    


def deletar_transacoes(ids):
    deletadas = 0

    try:
        for id in ids:
            transacao = session.query(Transacao).filter(Transacao.id == id).first()
            if transacao:
                session.delete(transacao)
                deletadas += 1

        if deletadas > 0:
            session.commit()
            if deletadas == 1:
                return "Transação deletada com sucesso"
            else:
                return f"{deletadas} transações deletadas com sucesso"
        else:
            return "Nenhuma transação encontrada para deletar"

    except Exception as e:
        session.rollback()
        return f"Erro ao deletar: {e}"

Base.metadata.create_all(engine)