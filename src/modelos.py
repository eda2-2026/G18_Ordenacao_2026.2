"""Modelos de dados e configurações de critérios de desempate."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

# Configuração centralizada da ordem dos critérios de desempate.
# Permite reconfigurar em um único ponto do sistema.
ORDEM_CRITERIOS: tuple[str, ...] = ("pontos", "vitorias", "saldo", "gols_pro")


def configurar_criterios(novos_criterios: Sequence[str]) -> None:
    """Configura globalmente a ordem dos critérios de desempate."""
    global ORDEM_CRITERIOS
    ORDEM_CRITERIOS = tuple(novos_criterios)


def obter_criterios() -> tuple[str, ...]:
    """Retorna a tupla de critérios de desempate atualmente configurada."""
    return ORDEM_CRITERIOS


@dataclass
class Time:
    """Representa um time na tabela de classificação."""

    nome: str
    pontos: int = 0
    vitorias: int = 0
    gols_pro: int = 0
    gols_contra: int = 0
    ataque: float = 1.0
    defesa: float = 1.0
    jogos: int = 0

    @property
    def saldo(self) -> int:
        """Calcula o saldo de gols (gols pró - gols contra)."""
        return self.gols_pro - self.gols_contra

    def chave(self, criterios: Sequence[str] | None = None) -> tuple:
        """Devolve a tupla de desempate de acordo com a ordem configurada.
        
        Por padrão, devolve (pontos, vitorias, saldo, gols_pro).
        """
        ordem = criterios if criterios is not None else ORDEM_CRITERIOS
        valores = []
        for crit in ordem:
            if crit == "saldo":
                valores.append(self.saldo)
            elif hasattr(self, crit):
                valores.append(getattr(self, crit))
            else:
                raise AttributeError(f"Critério desconhecido: {crit}")
        return tuple(valores)

    def copiar(self) -> Time:
        """Cria uma cópia rasa e rápida do time para simulações."""
        return Time(
            nome=self.nome,
            pontos=self.pontos,
            vitorias=self.vitorias,
            gols_pro=self.gols_pro,
            gols_contra=self.gols_contra,
            ataque=self.ataque,
            defesa=self.defesa,
            jogos=self.jogos,
        )


@dataclass
class Jogo:
    """Representa um confronto entre mandante e visitante."""

    mandante: str
    visitante: str


def calcular_forcas_ataque_defesa(times: Sequence[Time]) -> None:
    """Calcula as forças de ataque e defesa dos times a partir dos dados do campeonato:
    gols pró e contra por jogo divididos pela média de gols por jogo da liga.
    """
    total_jogos = sum(t.jogos for t in times)
    total_gols = sum(t.gols_pro for t in times)
    if total_jogos == 0 or total_gols == 0:
        return
    media_gols_por_jogo_liga = total_gols / total_jogos

    for t in times:
        if t.jogos > 0:
            t.ataque = round((t.gols_pro / t.jogos) / media_gols_por_jogo_liga, 4)
            t.defesa = round((t.gols_contra / t.jogos) / media_gols_por_jogo_liga, 4)


def carregar_classificacao(
    caminho_csv: str | Path,
    recalcular_forcas: bool = True,
) -> list[Time]:
    """Carrega a tabela de classificação a partir de um arquivo CSV."""
    caminho = Path(caminho_csv)
    times: list[Time] = []
    with caminho.open(mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            jogos = int(linha["jogos"]) if "jogos" in linha and linha["jogos"] else 0
            times.append(
                Time(
                    nome=linha["nome"].strip(),
                    pontos=int(linha["pontos"]),
                    vitorias=int(linha["vitorias"]),
                    gols_pro=int(linha["gols_pro"]),
                    gols_contra=int(linha["gols_contra"]),
                    ataque=float(linha.get("ataque", 1.0)),
                    defesa=float(linha.get("defesa", 1.0)),
                    jogos=jogos,
                )
            )

    total_gp = sum(t.gols_pro for t in times)
    total_gc = sum(t.gols_contra for t in times)
    if total_gp != total_gc:
        import warnings
        warnings.warn(
            f"Inconsistência nos dados de gols: total gols pró ({total_gp}) "
            f"!= total gols contra ({total_gc}).",
            UserWarning,
            stacklevel=2,
        )

    if recalcular_forcas and any(t.jogos > 0 for t in times):
        calcular_forcas_ataque_defesa(times)
    return times


def carregar_jogos(caminho_csv: str | Path) -> list[Jogo]:
    """Carrega os jogos restantes a partir de um arquivo CSV."""
    caminho = Path(caminho_csv)
    jogos: list[Jogo] = []
    with caminho.open(mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            jogos.append(
                Jogo(
                    mandante=linha["mandante"].strip(),
                    visitante=linha["visitante"].strip(),
                )
            )
    return jogos


def validar_jogos(times: Sequence[Time], jogos: Sequence[Jogo]) -> None:
    """Valida se todos os clubes dos confrontos constam na tabela de classificação."""
    nomes_cadastrados = {t.nome for t in times}
    for j in jogos:
        if j.mandante not in nomes_cadastrados:
            raise ValueError(
                f"Time mandante '{j.mandante}' no jogo contra '{j.visitante}' "
                f"não consta na tabela de classificação."
            )
        if j.visitante not in nomes_cadastrados:
            raise ValueError(
                f"Time visitante '{j.visitante}' no jogo contra '{j.mandante}' "
                f"não consta na tabela de classificação."
            )
