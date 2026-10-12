"""Módulo de ordenação da tabela de classificação (Insertion, Merge, Quick, Heap e Radix LSD)."""

from __future__ import annotations

from typing import Any, Callable, Sequence
from src.modelos import Time, obter_criterios


def _obter_chave_padrao(item: Any) -> Any:
    """Extrai a chave de desempate padrão do time ou retorna o próprio item."""
    if hasattr(item, "chave"):
        return item.chave()
    return item


def insertion_sort(
    lista: Sequence[Any],
    key: Callable[[Any], Any] | None = None,
    reverse: bool = True,
) -> list[Any]:
    """Ordena elementos inserindo cada item na posição correta do prefixo já ordenado.
    Complexidade: O(n) melhor caso, O(n²) médio e pior caso; O(1) de memória auxiliar.
    Estabilidade: Estável.
    """
    arr = list(lista)
    extrair = key if key is not None else _obter_chave_padrao

    for i in range(1, len(arr)):
        item = arr[i]
        chave_item = extrair(item)
        j = i - 1

        if reverse:
            # Em ordem decrescente, desloca elementos menores que o item atual
            while j >= 0 and extrair(arr[j]) < chave_item:
                arr[j + 1] = arr[j]
                j -= 1
        else:
            # Em ordem crescente, desloca elementos maiores que o item atual
            while j >= 0 and extrair(arr[j]) > chave_item:
                arr[j + 1] = arr[j]
                j -= 1

        arr[j + 1] = item

    return arr


def merge_sort(
    lista: Sequence[Any],
    key: Callable[[Any], Any] | None = None,
    reverse: bool = True,
) -> list[Any]:
    """Ordena por divisão e conquista, dividindo recursivamente ao meio e intercalando.
    Complexidade: O(n log n) em todos os casos; O(n) de memória auxiliar.
    Estabilidade: Estável.
    """
    if len(lista) <= 1:
        return list(lista)

    extrair = key if key is not None else _obter_chave_padrao
    meio = len(lista) // 2
    esquerda = merge_sort(lista[:meio], key=extrair, reverse=reverse)
    direita = merge_sort(lista[meio:], key=extrair, reverse=reverse)

    resultado: list[Any] = []
    i = j = 0

    while i < len(esquerda) and j < len(direita):
        chave_esq = extrair(esquerda[i])
        chave_dir = extrair(direita[j])

        if reverse:
            # Desempate estável: se esquerda[i] >= direita[j], preserva esquerda
            if chave_esq >= chave_dir:
                resultado.append(esquerda[i])
                i += 1
            else:
                resultado.append(direita[j])
                j += 1
        else:
            if chave_esq <= chave_dir:
                resultado.append(esquerda[i])
                i += 1
            else:
                resultado.append(direita[j])
                j += 1

    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


def quick_sort(
    lista: Sequence[Any],
    key: Callable[[Any], Any] | None = None,
    reverse: bool = True,
) -> list[Any]:
    """Ordena uma lista utilizando Quick Sort com particionamento de Hoare (Instável).
    
    Complexidade:
        Tempo: O(n log n) no caso médio e melhor caso; O(n^2) no pior caso.
               Utiliza o pivô central para mitigar pior caso em listas quase ordenadas.
        Espaço: O(log n) de pilha de recursão.
    Estabilidade:
        Instável devido às trocas entre extremidades no particionamento.
    """
    arr = list(lista)
    if len(arr) <= 1:
        return arr

    extrair = key if key is not None else _obter_chave_padrao

    def _quick_sort_rec(baixo: int, alto: int) -> None:
        if baixo < alto:
            pivo_idx = _particao_hoare(arr, baixo, alto, extrair, reverse)
            _quick_sort_rec(baixo, pivo_idx)
            _quick_sort_rec(pivo_idx + 1, alto)

    _quick_sort_rec(0, len(arr) - 1)
    return arr


def _particao_hoare(
    arr: list[Any],
    baixo: int,
    alto: int,
    extrair: Callable[[Any], Any],
    reverse: bool,
) -> int:
    """Particionamento de Hoare para Quick Sort."""
    meio = (baixo + alto) // 2
    chave_pivo = extrair(arr[meio])

    i = baixo - 1
    j = alto + 1

    while True:
        if reverse:
            while True:
                i += 1
                if extrair(arr[i]) <= chave_pivo:
                    break
            while True:
                j -= 1
                if extrair(arr[j]) >= chave_pivo:
                    break
        else:
            while True:
                i += 1
                if extrair(arr[i]) >= chave_pivo:
                    break
            while True:
                j -= 1
                if extrair(arr[j]) <= chave_pivo:
                    break

        if i >= j:
            return j

        arr[i], arr[j] = arr[j], arr[i]


def heap_sort(
    lista: Sequence[Any],
    key: Callable[[Any], Any] | None = None,
    reverse: bool = True,
) -> list[Any]:
    """Ordena construindo uma min-heap (para ordem decrescente) e extraindo a raiz sucessivamente.
    Complexidade: O(n log n) em todos os casos; O(1) de memória auxiliar.
    Estabilidade: Instável.
    """
    arr = list(lista)
    n = len(arr)
    if n <= 1:
        return arr

    extrair = key if key is not None else _obter_chave_padrao

    def _descer_min(raiz: int, tamanho: int) -> None:
        """Mantém a propriedade de Min-Heap (para ordenação decrescente)."""
        menor = raiz
        esq = 2 * raiz + 1
        dir = 2 * raiz + 2

        if esq < tamanho and extrair(arr[esq]) < extrair(arr[menor]):
            menor = esq
        if dir < tamanho and extrair(arr[dir]) < extrair(arr[menor]):
            menor = dir

        if menor != raiz:
            arr[raiz], arr[menor] = arr[menor], arr[raiz]
            _descer_min(menor, tamanho)

    def _descer_max(raiz: int, tamanho: int) -> None:
        """Mantém a propriedade de Max-Heap (para ordenação crescente)."""
        maior = raiz
        esq = 2 * raiz + 1
        dir = 2 * raiz + 2

        if esq < tamanho and extrair(arr[esq]) > extrair(arr[maior]):
            maior = esq
        if dir < tamanho and extrair(arr[dir]) > extrair(arr[maior]):
            maior = dir

        if maior != raiz:
            arr[raiz], arr[maior] = arr[maior], arr[raiz]
            _descer_max(maior, tamanho)

    if reverse:
        # 1. Constrói Min-Heap
        for i in range(n // 2 - 1, -1, -1):
            _descer_min(i, n)
        # 2. Extrai elementos da raiz para o final
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            _descer_min(0, i)
    else:
        # 1. Constrói Max-Heap
        for i in range(n // 2 - 1, -1, -1):
            _descer_max(i, n)
        # 2. Extrai elementos da raiz para o final
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            _descer_max(0, i)

    return arr


def radix_lsd_multicriterio(
    lista: Sequence[Time],
    criterios: Sequence[str] | None = None,
    desempate_nome: bool = False,
) -> list[Time]:
    """Ordena multicritérios via Counting Sort estável do menos ao mais importante (LSD).
    Complexidade: O(k * (n + b)), onde k é o nº de critérios e b a amplitude; O(n + b) auxiliar.
    Estabilidade: Estável.
    """
    arr = list(lista)
    if len(arr) <= 1:
        return arr

    ordem = list(criterios if criterios is not None else obter_criterios())

    # Passo preliminar: desempate determinístico por nome (A-Z)
    if desempate_nome:
        arr = insertion_sort(arr, key=lambda t: t.nome, reverse=False)

    # Ordena do critério MENOS importante para o MAIS importante (LSD)
    for crit in reversed(ordem):
        arr = _counting_sort_passada(arr, crit)

    return arr


def _obter_valor_criterio(time: Time, crit: str) -> int:
    """Recupera o valor inteiro de um critério para o time."""
    if crit == "saldo":
        return time.saldo
    if hasattr(time, crit):
        val = getattr(time, crit)
        if isinstance(val, int):
            return val
        return int(val)
    raise AttributeError(f"Critério inválido: {crit}")


def _counting_sort_passada(arr: list[Time], crit: str) -> list[Time]:
    """Executa uma passada estável de Counting Sort decrescente para um critério."""
    if not arr:
        return []

    valores = [_obter_valor_criterio(t, crit) for t in arr]
    min_v = min(valores)
    max_v = max(valores)
    amplitude = max_v - min_v  # M

    # Frequência de cada 'inv' (onde inv = amplitude - (val - min_v))
    # Tamanho do array de contagem é amplitude + 1
    contagem = [0] * (amplitude + 1)
    for val in valores:
        inv = amplitude - (val - min_v)
        contagem[inv] += 1

    # Acumula as contagens para obter posições prefixadas
    for i in range(1, amplitude + 1):
        contagem[i] += contagem[i - 1]

    # Preenche o array de saída da direita para a esquerda (garante estabilidade)
    saida: list[Time | None] = [None] * len(arr)
    for t in reversed(arr):
        val = _obter_valor_criterio(t, crit)
        inv = amplitude - (val - min_v)
        pos = contagem[inv] - 1
        saida[pos] = t
        contagem[inv] -= 1

    # Conversão de tipo garantida
    return [t for t in saida if t is not None]


ALGORITMOS: dict[str, Callable[..., list[Any]]] = {
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "heap": heap_sort,
    "radix": radix_lsd_multicriterio,
}


def ordenar_tabela(
    times: Sequence[Time],
    algoritmo: str = "merge",
    **kwargs: Any,
) -> list[Time]:
    """Interface unificada para ordenar a tabela de times pelo algoritmo escolhido."""
    alg = algoritmo.lower().strip()
    if alg not in ALGORITMOS:
        raise ValueError(
            f"Algoritmo desconhecido: '{algoritmo}'. Opções válidas: {list(ALGORITMOS.keys())}"
        )
    funcao = ALGORITMOS[alg]
    if alg != "radix" and "key" not in kwargs:
        # chave calculada uma vez + posição original como último critério
        chaves = {id(t): t.chave() + (-i,) for i, t in enumerate(times)}
        kwargs["key"] = lambda t: chaves[id(t)]
    return funcao(times, **kwargs)
