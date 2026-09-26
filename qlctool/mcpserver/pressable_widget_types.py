"""The widget types `live_press` may send a value to, in every language QLC+ 5 names them.

`getWidgetType` answers `VCWidget::typeToString`, which is translated
(`qmlui/virtualconsole/vcwidget.cpp`), so a Spanish QLC+ says "Boton" where an
English one says "Button". Read out of the qmlui `.ts` catalogues of the QLC+
clone at 531276f0 (2026-09-26). Only buttons and sliders take a bare value:
the same `<id>|255` starts audio capture on an Audio Triggers widget
(`webaccess-qml.cpp`), so every other type is refused.
"""

PRESSABLE_WIDGET_TYPES = frozenset(
    {
        # Button
        "Button",
        "Bot\xf3",
        "Bot\xf3n",
        "Bouton",
        "Knop",
        "Knopf",
        "Przycisk",
        "Pulsante",
        "Кнопка",
        "ボタン",
        # Slider
        "Slider",
        "Fader",
        "Schieberegler",
        "Suwak",
        "Слайдер",
        "フェダー",
    }
)
