"""Aplicação RSVP em Kivy com suporte multiplataforma."""
from __future__ import annotations

from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import DictProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from models import Guest
from storage import GuestRepository
from utils import is_valid_email, is_valid_phone, similar_names

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "data" / "guests.json"
EXPORT_FILE = APP_DIR / "exports" / "guests_export.csv"


class MessageBar(BoxLayout):
    """Componente para mostrar status ao usuário."""

    message = StringProperty("")
    level = StringProperty("info")


class FileSelectPopup(Popup):
    callback = ObjectProperty(None)

    def choose(self, selection: list[str]):
        if selection and self.callback:
            self.callback(selection[0])
        self.dismiss()


class RSVPApp(App):
    guest_count = NumericProperty(0)
    total_invites = NumericProperty(0)
    total_confirmed = NumericProperty(0)

    layout_mode = StringProperty("Clássico")
    theme_color = ListProperty([0.20, 0.45, 0.75, 1])
    logo_path = StringProperty("")

    guests: list[Guest]
    repo: GuestRepository

    theme_options = DictProperty(
        {
            "Azul": [0.20, 0.45, 0.75, 1],
            "Verde": [0.17, 0.62, 0.37, 1],
            "Roxo": [0.45, 0.31, 0.71, 1],
            "Escuro": [0.18, 0.18, 0.20, 1],
        }
    )

    def build(self):
        self.title = "RSVP Kivy"
        self.repo = GuestRepository(DATA_FILE)
        self.guests = self.repo.load_all()
        self.load_kv()
        Clock.schedule_once(lambda *_: self.refresh_counters(), 0)
        return self.root

    def load_kv(self):
        self.root = Builder.load_file(str(APP_DIR / "rsvp.kv"))

    def set_message(self, text: str, level: str = "info"):
        bar = self.root.ids.message_bar
        bar.message = text
        bar.level = level

    def refresh_counters(self):
        self.guest_count = len(self.guests)
        self.total_invites = sum(g.invited_count for g in self.guests)
        self.total_confirmed = sum(g.confirmed_count for g in self.guests)

    def save(self):
        self.repo.save_all(self.guests)
        self.refresh_counters()

    def add_guest(self, name: str, phone: str, email: str):
        name = name.strip()
        phone = phone.strip()
        email = email.strip()

        if not name:
            self.set_message("Nome é obrigatório.", "error")
            return
        if not is_valid_phone(phone):
            self.set_message("Telefone inválido. Use ao menos 8 dígitos.", "error")
            return
        if not is_valid_email(email):
            self.set_message("Email inválido.", "error")
            return

        if any(g.name.lower() == name.lower() for g in self.guests):
            self.set_message("Convidado já cadastrado.", "warning")
            return

        self.guests.append(Guest(name=name, phone=phone, email=email, invited_count=1, confirmed_count=0))
        self.save()
        self.set_message(f"Convidado '{name}' cadastrado com sucesso.", "success")

    def find_guest_exact(self, name: str) -> Guest | None:
        name = name.strip().lower()
        for g in self.guests:
            if g.name.lower() == name:
                return g
        return None

    def confirm_presence(self, typed_name: str, selected_suggestion: str = ""):
        lookup_name = selected_suggestion.strip() or typed_name.strip()
        guest = self.find_guest_exact(lookup_name)

        if guest is None:
            suggestions = similar_names(typed_name, [g.name for g in self.guests])
            if suggestions:
                self.root.ids.confirmation_screen.ids.suggestions.values = suggestions
                self.set_message("Nome não encontrado. Selecione uma sugestão.", "warning")
            else:
                self.root.ids.confirmation_screen.ids.suggestions.values = []
                self.set_message("Nenhum nome semelhante encontrado.", "error")
            return

        guest.confirmed_count += 1
        self.ask_companions(guest)
        self.save()
        self.root.ids.confirmation_screen.ids.suggestions.values = []
        self.set_message(f"Presença confirmada para {guest.name}.", "success")

    def ask_companions(self, guest: Guest):
        # Regra simples: cada confirmação pode adicionar acompanhantes extras.
        add_more = True
        while add_more:
            popup = CompanionPopup(on_submit=lambda qty: self._apply_companions(guest, qty))
            popup.open()
            add_more = False

    def _apply_companions(self, guest: Guest, qty: int):
        if qty > 0:
            guest.invited_count += qty
            guest.confirmed_count += qty
            self.set_message(f"{qty} acompanhante(s) adicionados para {guest.name}.", "success")
        self.save()

    def change_theme(self, theme_name: str):
        if theme_name in self.theme_options:
            self.theme_color = self.theme_options[theme_name]
            self.set_message(f"Tema alterado para {theme_name}.", "info")

    def change_layout(self, layout_name: str):
        self.layout_mode = layout_name
        self.set_message(f"Layout alterado para {layout_name}.", "info")

    def select_logo(self):
        popup = FileSelectPopup(callback=self._apply_logo)
        popup.open()

    def _apply_logo(self, filepath: str):
        if filepath.lower().endswith((".png", ".jpg", ".jpeg")):
            self.logo_path = filepath
            self.set_message("Logo carregada com sucesso.", "success")
        else:
            self.set_message("Arquivo inválido. Use PNG/JPG.", "error")

    def export_data(self):
        file_path = self.repo.export_csv(self.guests, EXPORT_FILE)
        self.set_message(f"Exportado para {file_path}", "success")


class CompanionPopup(Popup):
    on_submit = ObjectProperty(None)

    def submit(self, qty_text: str):
        try:
            qty = int(qty_text.strip() or "0")
            qty = max(0, qty)
        except ValueError:
            qty = 0

        if self.on_submit:
            self.on_submit(qty)
        self.dismiss()


if __name__ == "__main__":
    RSVPApp().run()
