# BORDEPAC — Design Spec
**Data:** 2026-03-10
**Status:** Aprovado

---

## Visão Geral

Jogo desktop estilo PAC-Man onde o jogador controla um **Border Collie** comendo **bolinhas de tênis** em um labirinto, fugindo (e eventualmente comendo) **Beagles** inimigos.

**Stack:** Python + Pygame
**Resolução:** 800x600px
**Tile size:** 32x32px (labirinto 25x18 células)

---

## Estrutura de Arquivos

```
BORDEPAC/
├── main.py              # Entry point, game loop principal
├── settings.py          # Constantes (tamanho tela, velocidades, cores)
├── game.py              # Classe Game — orquestra tudo
├── maze.py              # Classe Maze — renderiza labirinto, colisões
├── player.py            # Classe Player — Border Collie, movimento, animação
├── ghost.py             # Classe Ghost — Beagles, IA de perseguição
├── hud.py               # Pontuação, vidas, fase atual na tela
├── assets/
│   ├── sprites/         # PNGs do Border Collie e Beagles
│   ├── sounds/          # Efeitos sonoros (opcional)
│   └── fonts/           # Fonte do HUD
└── requirements.txt     # pygame
```

---

## Arquitetura

**Game Loop:** `main.py` → instancia `Game` → loop: `handle_events` → `update` → `draw` → repeat a 60 FPS.

**Labirinto:** Matriz 2D onde:
- `0` = caminho livre
- `1` = parede
- `2` = bolinha de tênis (pequena)
- `3` = power-up (bolinha grande)

O Border Collie e os Beagles se movem célula a célula no grid.

---

## Mecânicas

### Player (Border Collie)
- Move em 4 direções pelo grid
- Animação de boca abrindo/fechando ao comer (8-12 sprites: 2-3 frames × 4 direções)
- **Power mode** ao comer power-up: dura 10s (reduz 1s por fase, mínimo 3s)
- 3 vidas por jogo

### Ghosts — 4 Beagles com IA distinta
| Nome | Comportamento |
|------|---------------|
| **Biscuit** | Persegue diretamente o Border Collie |
| **Caramel** | Tenta cortar o caminho à frente do player |
| **Pepper** | Movimento semi-aleatório com tendência de cercar |
| **Nugget** | Fica longe quando player está perto, aproxima quando está distante |

Em power mode: Beagles ficam azuis e fogem. Se capturados: +200pts e voltam ao centro.

### Pontuação
| Evento | Pontos |
|--------|--------|
| Bolinha pequena | 10 pts |
| Power-up (bolinha grande) | 50 pts |
| 1º Beagle capturado | 200 pts |
| 2º Beagle consecutivo | 400 pts |
| 3º Beagle consecutivo | 800 pts |
| 4º Beagle consecutivo | 1600 pts |

### Progressão de Fases
- Mesmo labirinto em todas as fases
- Beagles ficam ~10% mais rápidos por fase
- Duração do power-up reduz 1s por fase (mínimo 3s)

---

## Visual

### Sprites (OpenGameArt — fallback: pygame.draw)
- **Border Collie:** 4 direções × 2-3 frames de animação de boca = 8-12 sprites (32x32px)
- **Beagles:** 4 direções + versão azul (power mode) + olhos piscando (modo saindo)
- Fallback: formas geométricas coloridas via `pygame.draw` — substituíveis depois

### Cores
- Fundo: preto / azul muito escuro
- Paredes: azul vibrante (estilo PAC-Man clássico)
- Bolinhas de tênis: círculos amarelo-esverdeados
- Power-ups: bolinhas maiores com brilho

### HUD
- **Esquerda:** pontuação
- **Centro:** número da fase
- **Direita:** ícones de vida (Border Collie miniatura)
- Tela de Game Over: "Apanhado!"
- Tela de vitória de fase: "Bola salva!"

---

## Assets — Fontes

- Sprites de cachorro: OpenGameArt.org (licença CC0/CC-BY)
- Fallback: geração procedural via `pygame.draw`

---

## Dependências

```
pygame>=2.0.0
```
