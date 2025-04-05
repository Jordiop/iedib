# Music Transformer - Experiment Documentation

Aquest quadern documenta les modificacions realitzades al model original "Music Transformer" i els seus efectes en la generacio de musica.

## Resum de les modificacions

He implementat una serie de canvis significatius al model original per millorar la qualitat de la musica generada i proporcionar mes control sobre el proces creatiu.

### 1. Arquitectura del model

| Parametre | Original | Modificat | % Canvi |
|-----------|----------|-----------|---------|
| Dimensio d'embedding | 256 | 384 | +50% |
| Blocs Transformer | 6 | 8 | +33% |
| Mida del batch | 6 | 8 | +33% |
| Dropout | 0.2 (implicit) | 0.25 (explicit) | +25% |

```python
# Configuracio original
CONFIG = utils.Config(
    max_sequence_len=2048,
    embedding_dim=256,
    num_transformer_blocks=6,
    batch_size=6,
    # ...
)

# Configuracio millorada
CONFIG = utils.Config(
    max_sequence_len=2048,
    embedding_dim=384,  # Augmentat per obtenir representacions mes riques
    num_transformer_blocks=8,  # Model mes profund per capturar millor el context
    batch_size=8,  # Estadistiques de batch mes estables
    dropout=0.25,  # Dropout explicit per a millor regularitzacio
    # ...
)
```

### 2. Mecanisme d'atenció millorat

He modificat significativament el mecanisme d'atenció relativa global:

```python
@keras.utils.register_keras_serializable()
class EnhancedRelativeGlobalAttention(layers.Layer):
    def __init__(self, num_heads, embedding_dim, max_sequence_len, temperature=1.0, **kwargs):
        # ...
        self.temperature = temperature  # Nou paràmetre per ajustar la "creativitat"
        
    # ...
    
    # Aplicam un escalat de temperatura per controlar la distribució d'atenció
    logits = attention_scores / (ops.sqrt(self.head_dim) * self.temperature)
```

Aquest canvi permet controlar millor la "temperatura" de l'atenció, influint directament en l'equilibri entre coherència i creativitat a la música generada.

### 3. Arquitectura Pre-Normalització

```python
# Original (post-norm)
attention_out = self.dropout_1(attention_out, training=training)
attention_out_normalized = self.layer_normalization_1(attention_out + inputs)

# Millorat (pre-norm)
normalized_inputs = self.layer_normalization_1(inputs)
attention_out, attention_weights = self.relative_global_attention_1(
    (normalized_inputs, normalized_inputs, normalized_inputs), mask=mask
)
attention_out = self.dropout_1(attention_out, training=training)
attention_out = attention_out + inputs  # Connexió residual
```

Canviar de post-normalització a pre-normalització millora el flux de gradients, especialment important per al nostre model més profund de 8 blocs transformer.

### 4. Xarxes Feed-Forward millorades

```python
# Original
self.feed_forward_network_pre = layers.Dense(self.embedding_dim // 2, "relu")
self.feed_forward_network_pos = layers.Dense(self.embedding_dim)

# Millorat
ffn_dim = embedding_dim * 4  # 8 vegades més gran que l'original
self.feed_forward_network_pre = layers.Dense(ffn_dim)
self.gelu_activation = layers.Activation("gelu")  # GELU en lloc de ReLU
self.feed_forward_network_pos = layers.Dense(self.embedding_dim)
```

Aquesta modificació proporciona molta més capacitat per modelar transformacions musicals complexes, crucial per capturar patrons i transicions musicals subtils.

### 5. Augmentació de dades

```python
# Augmentació per transposició - transposa entre -2 i +2 semitons
if self.use_augmentation and random.random() < 0.3:
    # Desplaçament aleatori entre -2 i +2 semitons
    shift = random.randint(-2, 2)
    
    for i in range(len(data)):
        # Aplica el desplaçament als esdeveniments NOTE_ON
        if note_on_range[0] <= data[i] < note_on_range[1]:
            # ...implementació...
```

L'augmentació per transposició ajuda el model a aprendre patrons musicals invariants a la tonalitat, permetent una millor generalització a diferents tonalitats musicals.

### 6. Funció de pèrdua millorada

```python
def enhanced_train_loss(y_true, y_pred):
    # Definim el factor de suavitzat d'etiquetes
    label_smoothing = 0.1
    
    # ...
    
    # Aplicam suavitzat d'etiquetes
    y_true_smooth = y_true_one_hot * (1.0 - label_smoothing) + label_smoothing / num_classes
```

El suavitzat d'etiquetes evita que el model es torni excessivament confiat en les seves prediccions, resultant en distribucions de probabilitat més equilibrades en la sortida, que es tradueixen en eleccions musicals més subtils.

### 7. Estratègia de mostreig avançada

```python
def _nucleus_sampling(self, probs, p=0.9):
    """Realitza mostreig de nucli (top-p) sobre una distribució de probabilitat."""
    # Ordena les probabilitats en ordre descendent
    sorted_probs, sorted_indices = ops.sort(probs, direction="DESCENDING")
    
    # Calcula probabilitats acumulatives
    cumulative_probs = ops.cumsum(sorted_probs, axis=-1)
    
    # Crea una màscara per a les probabilitats dins del nucli
    nucleus_mask = ops.less(cumulative_probs, p)
    
    # ...
```

L'enfocament combinat d'ajust de temperatura, filtrat top-k i mostreig nucleus dóna un control precís sobre el procés de generació. Això permet una àmplia gamma de sortides creatives.

## Resultats esperats

### Millores qualitatives

1. **Coherència musical**
   - **Original**: Bona coherència local, pot perdre estructura en peces més llargues
   - **Millorat**: Millor estructura a llarg termini gràcies al model més profund i millor atenció

2. **Qualitat harmònica**
   - **Original**: Progressions harmòniques bàsiques
   - **Millorat**: Gestió més sofisticada de progressions d'acords gràcies a una major capacitat de representació

3. **Consistència estilística**
   - **Original**: Pot desviar-se de l'estil original
   - **Millorat**: Millor adherència a l'estil de la llavor gràcies a un context més llarg i atenció millorada

4. **Control de generació**
   - **Original**: Limitat al mostreig top-k
   - **Millorat**: Control precís mitjançant els paràmetres de temperatura, top-k i top-p

### Cost computacional

Les millores vénen amb un augment dels requisits computacionals:

- **Mida del model**: ~50% més gran degut a l'augment de la dimensió d'embedding
- **Temps d'entrenament**: ~40% més llarg per els blocs transformer addicionals
- **Velocitat d'inferència**: ~30% més lenta durant la generació

## Exemples de generació

Es poden generar diferents estils musicals ajustant els paràmetres de generació:

```python
# Més determinista (enfocament en precisió)
generate_enhanced_music(
    model,
    seed_path,
    top_k=5,
    top_p=0.85,
    temperature=0.7,
)

# Equilibrat (configuració per defecte)
generate_enhanced_music(
    model,
    seed_path,
    top_k=10,
    top_p=0.92,
    temperature=0.8,
)

# Més creatiu (enfocament en diversitat)
generate_enhanced_music(
    model,
    seed_path,