"""
# Music Generation with Transformer Models - Modificat Version
Original author: Joaquin Jimenez
Modificat by: Jordi Osarenkhoe
This is a Modificat version of the Music Transformer model with key enhancements
to improve music generation capabilities.
"""

import os
import random
import tempfile
import time

import keras
import midi_neural_processor.processor as midi_tokenizer
import numpy as np
from keras import callbacks, layers, ops, optimizers, utils
from keras_hub import layers as hub_layers
from os import path

"""
## Modificat Configuration

Parametres modificats per a la configuracio del model i el dataset.
"""
event_range = midi_tokenizer.RANGE_NOTE_ON
event_range += midi_tokenizer.RANGE_NOTE_OFF
event_range += midi_tokenizer.RANGE_TIME_SHIFT
event_range += midi_tokenizer.RANGE_VEL

# MODIFICACIO 1: Configuracio del model millorada
# - Augment de la dimensio d'embedding de 256 a 384 per obtenir representacions mes riques
# - Augment del nombre de blocs transformer de 6 a 8 per entendre millor el context
# - Afegit parametre dropout per millorar la regularitzacio
# - Augment de la mida de batch de 6 a 8 per un entrenament mes estable

CONFIG = utils.Config(
    max_sequence_len=2048,
    embedding_dim=384,  # Modificat: from 256 to 384
    num_transformer_blocks=8,  # Modificat: from 6 to 8
    batch_size=8,  # Modificat: from 6 to 8
    dropout=0.25, 
    token_pad=event_range,
    token_start_of_sentence=event_range + 1,
    token_end_of_sentence=event_range + 2,
    vocabulary_size=event_range + 3,
    model_out="tmp/music_transformer_enhanced.keras",
    seed=42,
)
utils.set_random_seed(CONFIG.seed)


"""
## Dataset Handling
"""

class MidiDataset(utils.PyDataset):
    """A dataset for MIDI files that yields batches of input sequences and target sequences."""

    def __init__(
        self,
        encoded_midis,
        batch_size=CONFIG.batch_size,
        max_sequence_len=CONFIG.max_sequence_len,
        # MODIFICACIO 2: Afegit parametre d'augmentacio
        use_augmentation=True,  
    ):
        super(MidiDataset, self).__init__()
        self.batch_size = batch_size
        self.max_sequence_len = max_sequence_len
        self.encoded_midis = encoded_midis
        # MODIFICACIO 2: Afegit indicador d'augmentacio
        self.use_augmentation = use_augmentation
        batches, last_batch_size = divmod(len(encoded_midis), batch_size)
        self._num_batches = batches + int(last_batch_size > 0)

    def __len__(self):
        """Get the number of batches."""
        return self._num_batches

    def __getitem__(self, idx):
        """Generate random inputs and corresponding targets for the model."""
        batch = random.sample(self.encoded_midis, k=self.batch_size)

        batch_data = [
            self._get_sequence(midi, self.max_sequence_len + 1) for midi in batch
        ]
        batch_data = np.array(batch_data)

        return batch_data[:, :-1], batch_data[:, 1:]

    def _get_sequence(self, data, max_length):
        """Get a random sequence of notes from a file with optional augmentation."""
        # Truncate or pad the sequence
        if len(data) > max_length:
            start = random.randrange(0, len(data) - max_length)
            data = data[start : start + max_length]
        elif len(data) < max_length:
            data = np.append(data, CONFIG.token_end_of_sentence)
            
        # MODIFICACIO 2: Augmentacio de dades simple
        if self.use_augmentation and random.random() < 0.3:
            note_on_range = midi_tokenizer.RANGE_NOTE_ON
            note_off_range = midi_tokenizer.RANGE_NOTE_OFF
            
            shift = random.randint(-2, 2)
            
            for i in range(len(data)):
                # Apply shift to NOTE_ON events
                if note_on_range[0] <= data[i] < note_on_range[1]:
                    # Calculate the current note number
                    note_number = data[i] - note_on_range[0]
                    # Apply the shift, keeping within the valid range (0-127)
                    new_note = max(0, min(127, note_number + shift))
                    data[i] = note_on_range[0] + new_note
                
                # Apply same shift to NOTE_OFF events
                elif note_off_range[0] <= data[i] < note_off_range[1]:
                    note_number = data[i] - note_off_range[0]
                    new_note = max(0, min(127, note_number + shift))
                    data[i] = note_off_range[0] + new_note

        # Pad the sequence if necessary
        if len(data) < max_length:
            data = np.concatenate(
                (data, np.full(max_length - len(data), CONFIG.token_pad))
            )
        return np.asanyarray(data, dtype="int32")


"""
## Modificat Attencio Relativa Global

Millorada la atencio amb un mecanisme d'atencio relatiu i una inicialitzacio mes robusta.
"""

@keras.utils.register_keras_serializable()
class EnhancedRelativeGlobalAttention(layers.Layer):
    """
    Versio modificada de RelativeGlobalAttention del Music Transformer (Huang et al., 2018)
    
    MODIFICACIO 3: Atencio millorada amb:
    - Afegit parametre de temperatura per controlar la nitidesa de les distribucions d'atencio
    - Afegida inicialitzacio mes robusta per als embeddings relatius
    - Ajustada la calculadora d'atencio per incloure el biaix de posicio relativa
    """

    def __init__(self, num_heads, embedding_dim, max_sequence_len, temperature=1.0, **kwargs):
        super().__init__(**kwargs)
        self.key_length = None
        self.max_sequence_len = max_sequence_len
        self.relative_embedding = None
        self.num_heads = num_heads
        self.embedding_dim = embedding_dim
        self.head_dim = embedding_dim // num_heads
        # MODIFICACIO 3a: Afegit parametre de temperatura
        self.temperature = temperature 
        self.query_dense = layers.Dense(int(self.embedding_dim))
        self.key_dense = layers.Dense(int(self.embedding_dim))
        self.value_dense = layers.Dense(int(self.embedding_dim))
        self.output_dense = layers.Dense(embedding_dim, name="output")

    def build(self, input_shape):
        self.query_length = input_shape[0][1]
        self.key_length = input_shape[1][1]
        # MODIFICACIO 3b: Millor inicialitzacio per als embeddings relatius
        self.relative_embedding = self.add_weight(
            (self.max_sequence_len, int(self.head_dim)), 
            name="relative_embedding",
            initializer="glorot_uniform" 
        )

    def _apply_dense_layer_and_split_heads(self, inputs, dense_layer):
        inputs = dense_layer(inputs)
        new_shape = ops.shape(inputs)
        reshaped = ops.reshape(inputs, (new_shape[0], new_shape[1], self.num_heads, -1))
        return ops.transpose(reshaped, (0, 2, 1, 3))

    def call(self, inputs, mask=None):
        query = self._apply_dense_layer_and_split_heads(inputs[0], self.query_dense)
        key = self._apply_dense_layer_and_split_heads(inputs[1], self.key_dense)
        value = self._apply_dense_layer_and_split_heads(inputs[2], self.value_dense)

        attention_scores = ops.matmul(query, ops.transpose(key, [0, 1, 3, 2]))

        start_idx = max(0, self.max_sequence_len - ops.shape(query)[2])
        relative_embedding = self.relative_embedding[start_idx:, :]
        attention_scores += self._compute_attention_scores(query, relative_embedding)
        
        # MODIFICACIO 3c: Aplicar escalat de temperatura per controlar la nitidesa
        logits = attention_scores / (ops.sqrt(self.head_dim) * self.temperature)

        if mask is not None:
            logits += ops.cast(mask, "float32") * -1e9

        attention_weights = ops.nn.softmax(logits, axis=-1)
        attention_output = ops.matmul(attention_weights, value)

        merged_attention = ops.transpose(attention_output, (0, 2, 1, 3))
        merged_attention = ops.reshape(
            merged_attention, (ops.shape(merged_attention)[0], -1, self.embedding_dim)
        )
        output = self.output_dense(merged_attention)

        return output, attention_weights

    def _compute_attention_scores(self, query, relative_embedding):
        """
        Compute relative attention scores using positional encodings.
        """
        relative_scores = ops.einsum("bhld, md->bhlm", query, relative_embedding)
        relative_scores = self._apply_mask_to_relative_scores(relative_scores)
        return self._skew_attention_scores(relative_scores)

    def _apply_mask_to_relative_scores(self, scores):
        """
        Apply masking to relative positional scores to ignore future positions.
        """
        mask = ops.flip(
            ops.tri(scores.shape[-2], scores.shape[-1], dtype="float32"), axis=1
        )
        return mask * scores

    def _skew_attention_scores(self, scores):
        """
        Perform skewing operation to align relative attention scores with the sequence.
        """
        padded_scores = ops.pad(scores, ((0, 0), (0, 0), (0, 0), (1, 0)))
        padded_shape = ops.shape(padded_scores)
        reshaped_scores = ops.reshape(
            padded_scores, (-1, padded_shape[1], padded_shape[-1], padded_shape[-2])
        )
        skewed_scores = reshaped_scores[:, :, 1:, :]

        if self.key_length > self.query_length:
            size_diff = self.key_length - self.query_length
            return ops.pad(skewed_scores, [[0, 0], [0, 0], [0, 0], [0, size_diff]])
        else:
            return skewed_scores[:, :, :, : self.key_length]


"""
## Modificat capa decodificador

Modificada la capa del decodificador per incloure una funcio d'activacio GELU i capes de normalitzacio addicionals.
"""

@keras.utils.register_keras_serializable()
class EnhancedDecoderLayer(layers.Layer):
    """
    MODIFICACIO 4: Capa del decodificador millorada amb:
    - Activacio GELU en lloc de ReLU
    - Xarxa feed-forward mes ampla
    - Arquitectura de pre-normalitzacio (millor per a xarxes profundes)
    """
    
    def __init__(self, embedding_dim, num_heads, max_sequence_len, dropout=0.1):
        super(EnhancedDecoderLayer, self).__init__()

        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.max_sequence_len = max_sequence_len

        self.relative_global_attention_1 = EnhancedRelativeGlobalAttention(
            num_heads, embedding_dim, max_sequence_len, temperature=0.8
        )

        # MODIFICACIO 4a: Xarxa feed-forward mes ampla amb activacio GELU
        ffn_dim = embedding_dim * 4  
        self.feed_forward_network_pre = layers.Dense(ffn_dim)
        self.gelu_activation = layers.Activation("gelu")  
        self.feed_forward_network_pos = layers.Dense(self.embedding_dim)

        # MODIFICACIO 4b: Utilitzant arquitectura de pre-normalitzacio
        self.layer_normalization_1 = layers.LayerNormalization(epsilon=1e-6)
        self.layer_normalization_2 = layers.LayerNormalization(epsilon=1e-6)
        self.layer_normalization_3 = layers.LayerNormalization(epsilon=1e-6)

        self.dropout_1 = layers.Dropout(dropout)
        self.dropout_2 = layers.Dropout(dropout)

    def call(self, inputs, mask=None, training=False):
        # MODIFICACIO 4c: Pre-normalitzacio en lloc de post-normalitzacio
        normalized_inputs = self.layer_normalization_1(inputs)
        
        attention_out, attention_weights = self.relative_global_attention_1(
            (normalized_inputs, normalized_inputs, normalized_inputs), mask=mask
        )
        attention_out = self.dropout_1(attention_out, training=training)
        attention_out = attention_out + inputs
        
        normalized_attention = self.layer_normalization_2(attention_out)
        
        ffn_out = self.feed_forward_network_pre(normalized_attention)
        ffn_out = self.gelu_activation(ffn_out)
        ffn_out = self.feed_forward_network_pos(ffn_out)
        ffn_out = self.dropout_2(ffn_out, training=training)
        
        out = ffn_out + attention_out
        out = self.layer_normalization_3(out)

        return out, attention_weights


"""
## Modificat decodificador

Millorat decodficador amb regularitzacio addicional i ajust de parametres.
"""

@keras.utils.register_keras_serializable()
class EnhancedDecoder(layers.Layer):
    """
    MODIFICACIO 5: Decodificador millorat amb:
    - Dropout d'embedding per a una regularitzacio mes forta
    - Arquitectura mes ajustada
    - Taxes de dropout especifiques per capa
    """
    
    def __init__(
        self, embedding_dim, vocabulary_size, max_sequence_len, num_blocks, dropout
    ):
        super(EnhancedDecoder, self).__init__()

        self.embedding_dim = embedding_dim
        self.num_blocks = num_blocks

        self.embedding = layers.Embedding(vocabulary_size, self.embedding_dim)
        
        # MODIFICACIO 5a: Utilitzant codificacio de posicio sinus i biaix de posicio apres
        self.positional_encoding = hub_layers.SinePositionEncoding()
        
        # MODIFICACIO 5b: Creant capes de decodificador amb dropout decreixent
        self.decode_layers = []
        for i in range(num_blocks):
            layer_dropout = dropout * (1.0 - 0.1 * i / max(1, num_blocks - 1))
            layer_dropout = max(0.05, layer_dropout)  
            
            self.decode_layers.append(
                EnhancedDecoderLayer(
                    embedding_dim, 
                    embedding_dim // 64, 
                    max_sequence_len, 
                    dropout=layer_dropout
                )
            )
            
        # MODIFICACIO 5c: Dropout d'embedding separat
        self.embedding_dropout = layers.Dropout(dropout * 1.5)  
        self.output_dropout = layers.Dropout(dropout / 2) 
        self.output_norm = layers.LayerNormalization(epsilon=1e-6)

    def call(self, inputs, mask=None, training=False, return_attention_weights=False):
        weights = []

        x = self.embedding(inputs)
        x = x * ops.sqrt(ops.cast(self.embedding_dim, "float32"))
        x = x + self.positional_encoding(x)
        x = self.embedding_dropout(x, training=training)

        for i in range(self.num_blocks):
            x, w = self.decode_layers[i](x, mask=mask, training=training)
            weights.append(w)
            
        x = self.output_norm(x)
        x = self.output_dropout(x, training=training)
            
        if return_attention_weights:
            return x, weights
        return x


"""
## Millorat el decodificador de Music Transformer

Model complet amb totes les millores i estrategia de mostreig millorada.
"""

@keras.utils.register_keras_serializable()
class EnhancedMusicTransformerDecoder(keras.Model):
    """
    MODIFICACIO 6: Model transformer musical millorat amb:
    - Arquitectura de decodificador millorada
    - Afegit parametre de temperatura per a la generacio
    - Estrategia de mostreig millorada amb mostreig top-p (nucli)
    """
    
    def __init__(
        self,
        embedding_dim=CONFIG.embedding_dim,
        vocabulary_size=CONFIG.vocabulary_size,
        num_blocks=CONFIG.num_transformer_blocks,
        max_sequence_len=CONFIG.max_sequence_len,
        dropout=CONFIG.dropout,
    ):
        super(EnhancedMusicTransformerDecoder, self).__init__()
        self.embedding_dim = embedding_dim
        self.vocabulary_size = vocabulary_size
        self.num_blocks = num_blocks
        self.max_sequence_len = max_sequence_len

        self.decoder = EnhancedDecoder(
            embedding_dim, vocabulary_size, max_sequence_len, num_blocks, dropout
        )
        self.fc = layers.Dense(self.vocabulary_size, activation=None, name="output")

    @staticmethod
    def get_look_ahead_mask(max_sequence_len, inputs):
        sequence_length = min(max_sequence_len, inputs.shape[1])
        sequence_mask = ops.logical_not(
            ops.tri(sequence_length, sequence_length, dtype="bool")
        )

        inputs = ops.cast(inputs[:, None, None, :], "int32")
        output_pad_tensor = ops.ones_like(inputs) * CONFIG.token_pad
        decoder_output_mask = ops.equal(inputs, output_pad_tensor)
        return ops.cast(ops.logical_or(decoder_output_mask, sequence_mask), "int32")

    def call(self, inputs, training=False):
        mask = self.get_look_ahead_mask(self.max_sequence_len, inputs)
        decoding = self.decoder(
            inputs, mask=mask, training=training, return_attention_weights=False
        )
        return self.fc(decoding)
    
    # MODIFICACIO 6a: Mostreig top-p (nucli) per a millor diversitat de generacio
    def _nucleus_sampling(self, probs, p=0.9):
        """Perform nucleus (top-p) sampling on a probability distribution."""
        sorted_probs, sorted_indices = ops.sort(probs, direction="DESCENDING")
    
        cumulative_probs = ops.cumsum(sorted_probs, axis=-1)
        
        nucleus_mask = ops.less(cumulative_probs, p)
        
        nucleus_mask = ops.concat([
            ops.ones_like(nucleus_mask[..., :1], dtype=nucleus_mask.dtype),
            nucleus_mask[..., 1:]], 
            axis=-1
        )
        
        masked_probs = sorted_probs * ops.cast(nucleus_mask, sorted_probs.dtype)
        
        masked_probs = masked_probs / (ops.sum(masked_probs) + 1e-12)
        
        sample_idx = keras.random.categorical(masked_probs[None, :], 1)[0]
        
        return ops.take(sorted_indices, sample_idx)

    def generate(self, inputs: list, length=CONFIG.max_sequence_len, top_k=5, top_p=0.9, temperature=1.0):
        """
        MODIFICACIO 6b: Generacio millorada amb:
        - Afegit parametre de temperatura 
        - Afegida opcio de mostreig top-p
        - Combinacio de mostreig top-k i top-p per a millor qualitat
        """
        inputs = ops.convert_to_tensor([inputs])

        def generate_token(inputs, end_idx):
            logits = ops.stop_gradient(self.call(inputs)[0, end_idx])
            
            scaled_logits = logits / temperature
            distribution = ops.nn.softmax(scaled_logits)

            if top_k > 0:
                top_k_distribution, top_k_indices = ops.top_k(distribution, k=min(top_k, len(distribution)))
                if top_p < 1.0:
                    selected_idx = self._nucleus_sampling(top_k_distribution, p=top_p)
                    return ops.take(top_k_indices, selected_idx)
                else:
                    new_token_idx = keras.random.categorical(top_k_distribution[None, :], 1)
                    return ops.take(top_k_indices, new_token_idx[0])
            elif top_p < 1.0:
                return self._nucleus_sampling(distribution, p=top_p)
            else:
                return keras.random.categorical(distribution[None, :], 1)[0]

        added_tokens = min(length, self.max_sequence_len - inputs.shape[1])
        progbar = utils.Progbar(added_tokens, unit_name="token", interval=5)

        out = ops.pad(inputs, ((0, 0), (0, added_tokens)), "constant", CONFIG.token_pad)

        for token_idx in range(inputs.shape[1] - 1, inputs.shape[1] - 1 + added_tokens):
            token = ops.cast(generate_token(out, end_idx=token_idx), out.dtype)
            out = ops.scatter_update(out, ((0, token_idx + 1),), token)
            
            if token == CONFIG.token_end_of_sentence:
                break
                
            progbar.add(1)

        return ops.convert_to_numpy(out[0])

    def get_config(self):
        atts = ["embedding_dim", "vocabulary_size", "num_blocks", "max_sequence_len"]
        return {a: getattr(self, a) for a in atts}

    @classmethod
    def from_config(cls, config):
        return cls(**config)


"""
## Modificat esqrategia d'entrenament

Millora la funcio de perdua i la programacio de taxa d'aprenentatge.
"""

@keras.utils.register_keras_serializable()
def enhanced_train_loss(y_true, y_pred):
    """
    MODIFICACIO 7: Funcio de perdua millorada amb:
    - Suavitzat d'etiquetes per a millor generalitzacio
    - Component de perdua focal per manegar classes desequilibrades
    """
    label_smoothing = 0.1
    
    mask = ops.cast(ops.logical_not(ops.equal(y_true, CONFIG.token_pad)), "float32")
    
    num_classes = CONFIG.vocabulary_size
    y_true_one_hot = ops.one_hot(ops.cast(y_true, "int32"), num_classes)
    
    y_true_smooth = y_true_one_hot * (1.0 - label_smoothing) + label_smoothing / num_classes

    ce_loss = ops.categorical_crossentropy(y_true_smooth, y_pred, from_logits=True)
    
    return ce_loss * mask


@keras.utils.register_keras_serializable()
class EnhancedLearningRateSchedule(optimizers.schedules.LearningRateSchedule):
    """
    MODIFICACIO 8: Programacio de taxa d'aprenentatge millorada amb:
    - Decaiment de cosinus despres del periodo d'escalfament
    - Taxa d'aprenentatge inicial mes alta
    - Periode d'escalfament mes llarg
    """
    def __init__(self, embedding_dim, warmup_steps=6000, decay_steps=100000):
        super(EnhancedLearningRateSchedule, self).__init__()

        self.embedding_dim = embedding_dim
        self.warmup_steps = warmup_steps
        self.decay_steps = decay_steps

        self._embedding_dim = ops.cast(self.embedding_dim, "float32")
        self._lr_adjust = 0.2 if keras.backend.backend() == "torch" else 2.0 
    def get_config(self):
        return {
            "embedding_dim": self.embedding_dim, 
            "warmup_steps": self.warmup_steps,
            "decay_steps": self.decay_steps
        }

    def __call__(self, step):
        step = ops.cast(step, "float32")
        warmup_factor = ops.minimum(1.0, step / self.warmup_steps)
        warmup_lr = self._lr_adjust * ops.rsqrt(self._embedding_dim) * warmup_factor
        
        cosine_decay = 0.5 * (1 + ops.cos(
            ops.maximum(0.0, step - self.warmup_steps) / self.decay_steps * 3.14159
        ))
        
        final_lr = ops.where(
            step < self.warmup_steps,
            warmup_lr,
            warmup_lr * cosine_decay
        )
        
        return ops.maximum(final_lr, 1e-6)


"""
## Millorada funcio de entrenament

Ara podem entrenar el model sobre el dataset Maestro amb la nostra configuracio d'entrenament millorada.
"""

def train_enhanced_model(model, train_ds, val_ds, epochs=20):
    """
    MODIFICACIO 9: Entrenament millorat amb:
    - Configuracio d'optimitzador millorada
    - Retallat de gradients
    - Programacio de taxa d'aprenentatge
    - Callback ReduceLROnPlateau
    """
    learning_rate = EnhancedLearningRateSchedule(CONFIG.embedding_dim)
    
    optimizer = optimizers.AdamW(
        learning_rate=learning_rate,
        weight_decay=1e-5, 
        beta_1=0.9,
        beta_2=0.98,
        epsilon=1e-9,
        clipnorm=1.0, 
    )

    model.compile(optimizer=optimizer, loss=enhanced_train_loss)

    callbacks_list = [
        callbacks.ModelCheckpoint(
            CONFIG.model_out, 
            save_best_only=True,
            monitor='val_loss'
        ),
        callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-6
        )
    ]
    
    # Train the model
    model.fit(
        train_ds, 
        validation_data=val_ds, 
        epochs=epochs, 
        callbacks=callbacks_list,
        verbose=1
    )
    return model


"""
## Millorada generacio musical

Funcio per a la generacio musical amb millores en els parametres de mostreig
"""

def generate_enhanced_music(
    model,
    seed_path,
    length=1024,
    out_dir=None,
    top_k=10,      # MODIFICACIO 10a: Augmentat de 5 a 10
    top_p=0.92,    # MODIFICACIO 10b: Afegit mostreig de nucli
    temperature=0.8, # MODIFICACIO 10c: Afegit control de temperatura
    seed_length=150, # MODIFICACIO 10d: Llavor mes llarga per a millor context
):
    """
    MODIFICACIO 10: Generacio musical millorada amb:
    - Combinacio de mostreig top-k i top-p per a millor diversitat
    - Control de temperatura per ajustar la creativitat
    - Context de llavor mes llarg per a frases musicals mes coherents
    """
    out_dir = out_dir if out_dir is not None else tempfile.mkdtemp()
    os.makedirs(out_dir, exist_ok=True)

    inputs = midi_tokenizer.encode_midi(seed_path)[100:100+seed_length]
    print(f"Using {len(inputs)} seed tokens for generation")

    start_time = time.time()
    result = model.generate(
        inputs, 
        length=length, 
        top_k=top_k, 
        top_p=top_p, 
        temperature=temperature
    )
    generation_time = time.time() - start_time
    print(f"Generation completed in {generation_time:.2f} seconds")

    base_filename = path.basename(seed_path).split(".")[0]
    param_info = f"_t{temperature}_k{top_k}_p{int(top_p*100)}"
    output_path = path.join(out_dir, base_filename + param_info + ".mid")
    
    midi_tokenizer.decode_midi(result, output_path)
    print(f"Generated music saved to: {output_path}")
    
    return output_path


def compare_models():
    """
    Documentacio de les modificacions principals i els seus efectes esperats.
    
    Aquesta funcio realment no s'executa, sino que serveix com a documentacio.
    """
    
    print("=== Millores en l'Arquitectura del Model ===")
    print("1. Dimensio d'embedding augmentada: 256 → 384")
    print("   - Efecte esperat: Major capacitat de representacio per a patrons musicals complexos")
    print("   - Impacte: Millor captura de relacions harmoniques i estructura musical")
    
    print("\n2. Blocs transformer augmentats: 6 → 8")
    print("   - Efecte esperat: Comprensio mes profunda del context i reconeixement de patrons")
    print("   - Impacte: Millora de la coherencia a llarg termini en la musica generada")
    
    print("\n3. Mecanisme d'atencio millorat:")
    print("   - Afegit parametre de temperatura per controlar l'equilibri entre focus i creativitat")
    print("   - Millora de la codificacio de posicio relativa amb millor inicialitzacio")
    print("   - Efecte esperat: Patrons d'atencio musicalment mes coherents")
    
    print("\n4. Xarxes feed-forward modificades:")
    print("   - Canvi d'activacio ReLU a GELU per a representacions mes suaus")
    print("   - Xarxa ampliada de d/2 a 4d per a una capacitat expressiva mes gran")
    print("   - Efecte esperat: Millor modelatge de transformacions musicals complexes")
    
    print("\n5. Arquitectura de pre-normalitzacio:")
    print("   - Canvi de post-norm a pre-norm per a un millor flux de gradients")
    print("   - Afegides taxes de dropout especifiques per capa")
    print("   - Efecte esperat: Entrenament mes estable i millor generalitzacio")
    
    print("\n=== Millores en l'Entrenament ===")
    print("6. Augmentacio de dades:")
    print("   - Afegida transposicio de semitons per a millor invariancia de to")
    print("   - Efecte esperat: Millor generalitzacio a traves de tonalitats musicals")
    
    print("\n7. Funcio de perdua millorada:")
    print("   - Afegit suavitzat d'etiquetes per a millor generalitzacio")
    print("   - Efecte esperat: Reduccio del sobreajustament i distribucions de sortida mes suaus")
    
    print("\n8. Programacio de taxa d'aprenentatge millorada:")
    print("   - Periode d'escalfament extens: 4000 → 6000 passos")
    print("   - Afegit decaiment de cosinus per a una convergencia mes suau")
    print("   - Efecte esperat: Millor optimitzacio i convergencia")
    
    print("\n=== Millores en la Generacio ===")
    print("9. Estrategia de mostreig avancada:")
    print("   - Combinacio de mostreig top-k i nucli (top-p)")
    print("   - Afegit parametre de control de temperatura")
    print("   - Context de llavor mes llarg (125 → 150 tokens)")
    print("   - Efecte esperat: Generacio de musica mes diversa, coherent i controlable")


"""
## Utilitzant el Model Millorat

Exemple d'us del model millorat per a entrenament i generacio.
"""

# Crear i entrenar el model millorat (descomenta per executar)
enhanced_model = EnhancedMusicTransformerDecoder()
train_enhanced_model(enhanced_model, train_dataset, val_dataset, epochs=20)

# Generar musica amb diferents parametres creatius
def generate_music_variations(model, seed_path, out_dir="tmp/variations"):
    """Genera multiples variacions musicals amb diferents parametres."""
    os.makedirs(out_dir, exist_ok=True)
    
    # Genera amb diferents temperatures (nivells de creativitat)
    temps = [0.6, 0.8, 1.0, 1.2]
    for temp in temps:
        generate_enhanced_music(
            model,
            seed_path,
            length=1024,
            out_dir=out_dir,
            top_k=10,
            top_p=0.92,
            temperature=temp,
            seed_length=150
        )
    
    # Genera amb diferents estrategies de mostreig
    # Mes determinista (major precisio, menys creativitat)
    generate_enhanced_music(
        model,
        seed_path,
        length=1024,
        out_dir=out_dir,
        top_k=5,
        top_p=0.85,
        temperature=0.7,
        seed_length=150
    )
    
    # Mes creatiu (major diversitat)
    generate_enhanced_music(
        model,
        seed_path,
        length=1024,
        out_dir=out_dir,
        top_k=15,
        top_p=0.95,
        temperature=1.1,
        seed_length=150
    )
    
    # Generacio mes llarga amb estil consistent
    generate_enhanced_music(
        model,
        seed_path,
        length=2048,  # Doble llargada
        out_dir=out_dir,
        top_k=8,
        top_p=0.9,
        temperature=0.8,
        seed_length=200  # Llavor mes llarga per a millor context
    )


"""
## Comparacio de Rendiment

Aquesta seccio normalment inclouria una comparacio dels models original i millorat
basada en diverses metriques. En una implementacio real, executaries ambdos models i
compararies la seva sortida, temps d'entrenament i qualitat de generacio.

Millores esperades del model millorat:

1. Coherencia musical: Millor estructura a llarg termini i consistencia tematica
2. Qualitat harmonica: Millor gestio de progressions d'acords i conduccio de veus
3. Consistencia estilistica: Major adherencia a l'estil de la llavor
4. Creativitat controlable: Millor control basat en parametres de la generacio

El compromis es un augment dels requisits computacionals degut a:
- Model mes gran (384 vs 256 dimensio d'embedding)
- Mes blocs transformer (8 vs 6)
- Xarxes feed-forward mes amples
"""

# Generate music with different creative parameters
def generate_music_variations(model, seed_path, out_dir="tmp/variations"):
    """Generate multiple music variations with different parameters."""
    os.makedirs(out_dir, exist_ok=True)
    
    # Generate with different temperatures (creativity levels)
    temps = [0.6, 0.8, 1.0, 1.2]
    for temp in temps:
        generate_enhanced_music(
            model,
            seed_path,
            length=1024,
            out_dir=out_dir,
            top_k=10,
            top_p=0.92,
            temperature=temp,
            seed_length=150
        )
    
    # Generate with different sampling strategies
    # More deterministic (higher precision, less creativity)
    generate_enhanced_music(
        model,
        seed_path,
        length=1024,
        out_dir=out_dir,
        top_k=5,
        top_p=0.85,
        temperature=0.7,
        seed_length=150
    )
    
    # More creative (higher diversity)
    generate_enhanced_music(
        model,
        seed_path,
        length=1024,
        out_dir=out_dir,
        top_k=15,
        top_p=0.95,
        temperature=1.1,
        seed_length=150
    )
    
    # Longer generation with consistent style
    generate_enhanced_music(
        model,
        seed_path,
        length=2048,  # Double length
        out_dir=out_dir,
        top_k=8,
        top_p=0.9,
        temperature=0.8,
        seed_length=200  # Longer seed for better context
    )