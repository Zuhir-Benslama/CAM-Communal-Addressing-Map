"""Chart generation mixins for panel and numbering distribution plots."""

import logging

import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib.ticker import MaxNLocator
from sqlalchemy import func

from qgis.core import QgsProject

from ..models import get_session, PanelSign, Numbering
from ..constants import LAYER_PANELS, LAYER_NUMBERING, CHART_SVG

logger = logging.getLogger(__name__)


CHART_COLOR = 'yellow'


def _render_bar_chart(results, xlabel: str, ylabel: str, title: str) -> None:
    """Render a bar chart from query results and save to CHART_SVG."""
    reshaper = arabic_reshaper.ArabicReshaper(
        configuration={
            'delete_harakat': False,
            'support_ligatures': True,
            'RIAL_SIGN': True,
        },
    )

    labels = [get_display(reshaper.reshape(str(row[0]))) for row in results]
    counts = [row[1] for row in results]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color=CHART_COLOR)

    plt.xlabel(get_display(reshaper.reshape(xlabel)))
    plt.ylabel(get_display(reshaper.reshape(ylabel)))
    plt.title(get_display(reshaper.reshape(title)))

    ax = plt.gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()
    plt.savefig(CHART_SVG, format='svg')


def _toggle_layer_visibility(layer_name: str, visible: bool) -> None:
    """Show or hide a named layer in the layer tree."""
    layer = QgsProject.instance().mapLayersByName(layer_name)
    if layer:
        layer = layer[0]
        root = QgsProject.instance().layerTreeRoot()
        node = root.findLayer(layer.id())
        if node:
            node.setItemVisibilityChecked(visible)


class ChartMixin:
    """Mixin providing chart generation for panel and numbering data."""

    def carte_pano1(self) -> None:
        """Generate a bar chart showing panel sign distribution by situation."""
        self.type_plan = LAYER_PANELS
        self.type_to_hide = LAYER_NUMBERING
        session = get_session()
        try:
            results = session.query(
                PanelSign.Stituation,
                func.count().label('count')
            ).group_by(PanelSign.Stituation).all()
        finally:
            session.close()

        _render_bar_chart(
            results,
            xlabel=self._tr('الوضعية'),
            ylabel=self._tr('العدد'),
            title=self._tr('التوزيع حسب الوضعية'),
        )

        _toggle_layer_visibility(LAYER_PANELS, True)
        _toggle_layer_visibility(LAYER_NUMBERING, False)

    def carte_num1(self) -> None:
        """Generate a bar chart showing numbering distribution by state."""
        self.type_plan = LAYER_NUMBERING
        self.type_to_hide = LAYER_PANELS
        session = get_session()
        try:
            results = session.query(
                Numbering.etat,
                func.count().label('count')
            ).group_by(Numbering.etat).all()
        finally:
            session.close()

        _render_bar_chart(
            results,
            xlabel=self._tr('الحالة'),
            ylabel=self._tr('العدد'),
            title=self._tr('التوزيع حسب حالة الترقيم'),
        )

        _toggle_layer_visibility(LAYER_NUMBERING, True)
        _toggle_layer_visibility(LAYER_PANELS, False)

    def get_zone_chart(self, wilaya_number: int) -> None:
        """Generate a chart for zone type distribution in a wilaya."""
        from ..db.operations import get_zone_distribution
        results = get_zone_distribution(wilaya_number)
        if not results:
            logger.warning(
                "No data available for wilaya number: %s", wilaya_number,
            )
            return

        _render_bar_chart(
            results,
            xlabel=self._tr('الوضعية'),
            ylabel=self._tr('العدد'),
            title=self._tr('التوزيع حسب الوضعية'),
        )

        _toggle_layer_visibility(LAYER_PANELS, False)
        _toggle_layer_visibility(LAYER_NUMBERING, True)
