import numpy as np


def processar_scan(leituras_lidar):
    """
    Processa 360 leituras de um sensor LiDAR.

    Retorna a menor distância válida nos setores:
        Frente:    345° a 15°
        Esquerda:   45° a 135°
        Direita:   225° a 315°

    Leituras válidas:
        >= 0.1 m
        <= 5.0 m
    """

    # Converte a lista para um array NumPy
    leituras = np.array(leituras_lidar, dtype=float)

    # Verifica se existem exatamente 360 leituras
    if len(leituras) != 360:
        raise ValueError("O LiDAR deve possuir exatamente 360 leituras.")

    # Remove valores inválidos:
    # - menores que 0.1 m
    # - maiores que 5.0 m
    # - valores NaN ou infinitos
    validas = (
        np.isfinite(leituras) &
        (leituras >= 0.1) &
        (leituras <= 5.0)
    )

    # =====================================================
    # SETOR DA FRENTE
    # 345° até 359° + 0° até 15°
    # =====================================================

    indices_frente = list(range(345, 360)) + list(range(0, 16))

    # Seleciona somente as leituras válidas
    frente = leituras[indices_frente]
    frente_validas = frente[validas[indices_frente]]

    # =====================================================
    # SETOR DA ESQUERDA
    # 45° até 135°
    # =====================================================

    indices_esquerda = list(range(45, 136))

    esquerda = leituras[indices_esquerda]
    esquerda_validas = esquerda[validas[indices_esquerda]]

    # =====================================================
    # SETOR DA DIREITA
    # 225° até 315°
    # =====================================================

    indices_direita = list(range(225, 316))

    direita = leituras[indices_direita]
    direita_validas = direita[validas[indices_direita]]

    # =====================================================
    # ENCONTRA A MENOR DISTÂNCIA
    # =====================================================

    min_frente = np.min(frente_validas) if len(frente_validas) > 0 else None
    min_esquerda = np.min(esquerda_validas) if len(esquerda_validas) > 0 else None
    min_direita = np.min(direita_validas) if len(direita_validas) > 0 else None

    # Retorna os resultados
    return {
        'frente': min_frente,
        'esquerda': min_esquerda,
        'direita': min_direita
    }


# =====================================================
# TESTE DO PROGRAMA
# =====================================================

# Cria 360 leituras inicialmente com 3 metros
leituras = np.full(360, 3.0)

# Coloca alguns valores inválidos
leituras[10] = 0.0
leituras[50] = 0.05
leituras[100] = 6.0
leituras[250] = np.inf

# Coloca obstáculos válidos
leituras[5] = 1.2       # Frente
leituras[80] = 2.0      # Esquerda
leituras[270] = 0.8     # Direita

# Processa o LiDAR
resultado = processar_scan(leituras)

# Mostra o resultado
print("Resultado do processamento:")
print(f"Frente:    {resultado['frente']:.2f} m")
print(f"Esquerda:  {resultado['esquerda']:.2f} m")
print(f"Direita:   {resultado['direita']:.2f} m")
