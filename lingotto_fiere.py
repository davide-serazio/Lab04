from csv import reader

class Espositore:
    def __init__(self, codice, nome, cognome):
        self.codice = codice
        self.nome = nome
        self.cognome = cognome

    def __eq__(self, other):
        if isinstance(other, Espositore): # isinstance(oggetto, Classe) Restituisce True se l’oggetto è un’istanza di quella classe, oppure di una sua sottoclasse; altrimenti restituisce False
            # quindi controlliamo che other sia un Espositore
            return self.codice == other.codice
        return False

    def __str__(self):
        return f"{self.codice}: {self.nome} {self.cognome}"

class Stand:
    # Classe base: rappresenta uno stand Standard
    tipo = "Standard"

    def __init__(self, codice, padiglione, superficie, prezzo_base):
        self.codice = codice
        self.padiglione = padiglione
        self.superficie = superficie
        self.prezzo_base = prezzo_base
        self.disponibile = True
        self.espositore = None

    def calcola_prezzo(self):
        return self.prezzo_base

    def __eq__(self, other):
        if isinstance(other, Stand):
            return self.codice == other.codice
        return False

    def __lt__(self, other):
        # sorted() usa questo metodo per confrontare i prezzi FINALI.
        return self.calcola_prezzo() < other.calcola_prezzo()

    def __str__(self):
        stato = "Disponibile"
        if not self.disponibile:
            stato = f"Assegnato a {self.espositore}"

        testo = f"{self.codice}: {self.tipo} | {self.superficie} mq - "
        testo += f"Padiglione {self.padiglione} - "
        testo += f"Prezzo {self.calcola_prezzo():.2f} euro - {stato}"
        return testo

class StandConPrese(Stand):
    tipo = "Prese Extra"

    def __init__(self, codice, padiglione, superficie, prezzo_base, numero_prese):
        super().__init__(codice, padiglione, superficie, prezzo_base)
        self.numero_prese = numero_prese

    def calcola_prezzo(self):
        # Override: ogni presa aggiunge il 7% del prezzo base
        return self.prezzo_base * (1 + 0.07 * self.numero_prese)

    def __str__(self):
        return super().__str__() + f" - Prese aggiuntive: {self.numero_prese}"


class StandPremium(Stand):
    tipo = "Premium"

    def __init__(self, codice, padiglione, superficie, prezzo_base, posizione):
        super().__init__(codice, padiglione, superficie, prezzo_base)
        self.posizione = posizione

    def calcola_prezzo(self):
        return self.prezzo_base * 1.30

    def __str__(self):
        return super().__str__() + f" - Posizione: {self.posizione}"


class LingottoFiere:
    def __init__(self, nome):
        self.set_nome(nome)
        # Dizionari: codice identificativo -> oggetto corrispondente.
        self.stand = {}
        self.espositori = {}

    def get_nome(self):
        return self._nome

    def set_nome(self, nome):
        nome = nome.strip()
        if not nome:
            raise ValueError("Il nome del centro non può essere vuoto.")
        self._nome = nome

    def __str__(self):
        testo = f"{self._nome}: {len(self.stand)} stand, "
        testo += f"{len(self.espositori)} espositori"
        return testo

    def carica_file_dati(self, file_path):
        # I dati vengono sostituiti solo dopo aver letto tutto il file.
        # Un nuovo caricamento riuscito azzera le precedenti assegnazioni.
        nuovi_stand = {}
        nuovi_espositori = {}

        # Se il file manca, open() solleva FileNotFoundError.
        with open(file_path, "r", encoding="utf-8") as file:
            for campi in reader(file):
                if not campi:  # Ignora le righe vuote.
                    continue

                campi_puliti = []
                for campo in campi:
                    campi_puliti.append(campo.strip())
                campi = campi_puliti

                if len(campi) == 1 and not campi[0]: # controllo che gestisce anche una riga che conteneva soltanto spazi
                    continue

                for campo in campi:
                    if campo == "":
                        raise ValueError("Sono presenti campi vuoti.")

                codice = campi[0].upper()

                if codice.startswith("ST"):
                    if len(campi) != 4 and len(campi) != 5:
                        raise ValueError("Uno stand richiede 4 o 5 campi.")

                    if codice in nuovi_stand:
                        raise ValueError(f"Codice duplicato: {codice}.")

                    superficie = float(campi[1])
                    padiglione = int(campi[2])
                    prezzo_base = float(campi[3])

                    if superficie <= 0 or padiglione <= 0 or prezzo_base < 0:
                        raise ValueError("Dati numerici dello stand non validi.")

                    if len(campi) == 4:
                        stand = Stand(
                            codice, padiglione, superficie, prezzo_base
                        )

                    else:
                        extra = campi[4]

                        # Distingue un numero intero da una posizione testuale.
                        try:
                            numero_prese = int(extra)
                            extra_numerico = True
                        except ValueError:
                            extra_numerico = False

                        if extra_numerico:
                            if numero_prese < 0:
                                raise ValueError("Il numero di prese è negativo.")

                            stand = StandConPrese(
                                codice, padiglione, superficie,
                                prezzo_base, numero_prese
                            )
                        else:
                            stand = StandPremium(
                                codice, padiglione, superficie,
                                prezzo_base, extra
                            )

                    nuovi_stand[codice] = stand # Per esempio, alla chiave "ST2" viene associato l’oggetto StandConPrese appena creato

                elif codice.startswith("ES"):
                    if len(campi) != 3:
                        raise ValueError("Un espositore richiede 3 campi.")

                    if codice in nuovi_espositori:
                        raise ValueError(f"Codice duplicato: {codice}.")

                    nuovi_espositori[codice] = Espositore(
                        codice, campi[1], campi[2]
                    )

                else:
                    raise ValueError(f"Codice non riconosciuto: {codice}.")

        self.stand = nuovi_stand
        self.espositori = nuovi_espositori

    def assegna_stand_a_espositore(self, codice_stand, codice_espositore):
        codice_stand = codice_stand.strip().upper()
        codice_espositore = codice_espositore.strip().upper()

        if codice_stand not in self.stand:
            raise ValueError("Lo stand indicato non esiste.")

        if codice_espositore not in self.espositori:
            raise ValueError("L'espositore indicato non esiste.")

        # Recuperiamo gli oggetti corrispondenti
        stand = self.stand[codice_stand]
        espositore = self.espositori[codice_espositore]

        if not stand.disponibile:
            raise ValueError("Lo stand è già occupato.")

        for altro_stand in self.stand.values(): # self.stand.values() permette di scorrere gli oggetti stand contenuti nel dizionario
            # Il confronto usa __eq__ della classe Espositore.
            if altro_stand.espositore == espositore:
                raise ValueError("L'espositore ha già uno stand assegnato.")

        # Modifica lo stato soltanto dopo aver superato tutti i controlli.
        stand.espositore = espositore
        stand.disponibile = False

    def elenca_espositori(self):
        # Il metodo elenca_espositori stampa ogni espositore e cerca il suo eventuale stand
        if not self.espositori:
            print("Nessun espositore caricato.")
            return

        for espositore in self.espositori.values():
            assegnazione = "Nessuno stand assegnato"

            for stand in self.stand.values():
                if stand.espositore == espositore:
                    assegnazione = f"Stand assegnato: {stand.codice}"
                    break

            print(f"{espositore} - {assegnazione}")

    def stand_ordinati_per_prezzo(self):
        # Restituisce una nuova lista, usando Stand.__lt__.
        return sorted(self.stand.values())