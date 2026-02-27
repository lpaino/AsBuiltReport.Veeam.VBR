# RSVP Kivy (Desktop + Mobile)

Sistema RSVP em Python/Kivy com:
- Configuração visual (tema, layout e upload de logo).
- Cadastro de convidados com validações básicas.
- Confirmação de presença com busca exata e sugestões por similaridade.
- Contadores em tempo real (convidados, convites e confirmações).
- Exportação CSV.

## Requisitos

```bash
pip install kivy
```

## Executar

```bash
cd rsvp_kivy
python main.py
```

## Compilação multiplataforma

- **Windows/macOS/Linux**: empacotar com PyInstaller/Nuitka.
- **Android**: usar Buildozer (Linux) + python-for-android.
- **iOS**: usar kivy-ios em macOS.

> Estrutura modular: `main.py` (UI + fluxo), `models.py` (dados), `storage.py` (persistência/exportação), `utils.py` (validação e similaridade).
