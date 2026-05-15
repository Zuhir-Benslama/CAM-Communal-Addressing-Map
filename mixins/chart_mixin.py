"""Chart generation mixins for panel and numbering distribution plots."""

from sqlalchemy import func

from qgis.core import QgsProject

from ..models import get_session, PanelSign, Numbering
from ..constants import LAYER_PANELS, LAYER_NUMBERING, CHART_SVG


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

        import matplotlib.pyplot as plt
        import arabic_reshaper
        from bidi.algorithm import get_display
        from matplotlib.ticker import MaxNLocator
        reshaping_config = {
            'delete_harakat': False,
            'support_ligatures': True,
            'RIAL_SIGN': True,
        }

        reshaper = arabic_reshaper.ArabicReshaper(
            configuration=reshaping_config,
        )

        labels = [get_display(reshaper.reshape(str(row[0]))) for row in results]
        counts = [row[1] for row in results]

        plt.figure(figsize=(10, 6))
        plt.bar(labels, counts, color='yellow')

        plt.xlabel(get_display(reshaper.reshape('الوضعية')))
        plt.ylabel(get_display(reshaper.reshape('العدد')))
        plt.title(
            get_display(reshaper.reshape('التوزيع حسب الوضعية')),
        )

        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.tight_layout()
        plt.savefig(CHART_SVG, format='svg')

        layer = QgsProject.instance().mapLayersByName(LAYER_PANELS)
        if layer:
            layer = layer[0]
            root = QgsProject.instance().layerTreeRoot()
            node = root.findLayer(layer.id())
            if node:
                node.setItemVisibilityChecked(False)

        layer = QgsProject.instance().mapLayersByName(LAYER_NUMBERING)
        if layer:
            layer = layer[0]
            root = QgsProject.instance().layerTreeRoot()
            node = root.findLayer(layer.id())
            if node:
                node.setItemVisibilityChecked(True)

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

        import matplotlib.pyplot as plt
        import arabic_reshaper
        from bidi.algorithm import get_display
        from matplotlib.ticker import MaxNLocator
        reshaping_config = {
            'delete_harakat': False,
            'support_ligatures': True,
            'RIAL_SIGN': True,
        }

        reshaper = arabic_reshaper.ArabicReshaper(
            configuration=reshaping_config,
        )

        labels = [get_display(reshaper.reshape(str(row[0]))) for row in results]
        counts = [row[1] for row in results]

        plt.figure(figsize=(10, 6))
        plt.bar(labels, counts, color='yellow')

        plt.xlabel(get_display(reshaper.reshape('الحالة')))
        plt.ylabel(get_display(reshaper.reshape('العدد')))
        plt.title(
            get_display(reshaper.reshape('التوزيع حسب حالة الترقيم')),
        )

        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.tight_layout()
        plt.savefig(CHART_SVG, format='svg')

        layer = QgsProject.instance().mapLayersByName(LAYER_NUMBERING)
        if layer:
            layer = layer[0]
            root = QgsProject.instance().layerTreeRoot()
            node = root.findLayer(layer.id())
            if node:
                node.setItemVisibilityChecked(False)

        layer = QgsProject.instance().mapLayersByName(LAYER_PANELS)
        if layer:
            layer = layer[0]
            root = QgsProject.instance().layerTreeRoot()
            node = root.findLayer(layer.id())
            if node:
                node.setItemVisibilityChecked(True)

    def get_zone_chart(self, wilaya_number: int) -> None:
        """Generate a chart for zone type distribution in a wilaya."""
        from ..db.operations import get_zone_distribution
        import logging
        logger = logging.getLogger(__name__)
        import matplotlib.pyplot as plt
        import arabic_reshaper
        from bidi.algorithm import get_display
        from matplotlib.ticker import MaxNLocator

        results = get_zone_distribution(wilaya_number)
        if not results:
            logger.warning(
                "No data available for wilaya number: %s", wilaya_number,
            )
            return

        reshaping_config = {
            'use_unshaped_instead_of_isolated': True,
            'support_ligatures': True,
            'RIAL_SIGN': True,
        }

        reshaper = arabic_reshaper.ArabicReshaper(
            configuration=reshaping_config,
        )

        labels = [get_display(reshaper.reshape(str(row[0]))) for row in results]
        counts = [row[1] for row in results]

        plt.figure(figsize=(10, 6))
        plt.bar(labels, counts, color='yellow')

        plt.xlabel(get_display(reshaper.reshape('الوضعية')))
        plt.ylabel(get_display(reshaper.reshape('العدد')))
        plt.title(
            get_display(reshaper.reshape('التوزيع حسب الوضعية')),
        )

        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.tight_layout()
        plt.savefig(CHART_SVG, format='svg')

        layer = QgsProject.instance().mapLayersByName(LAYER_PANELS)
        if layer:
            layer = layer[0]
            root = QgsProject.instance().layerTreeRoot()
            node = root.findLayer(layer.id())
            if node:
                node.setItemVisibilityChecked(False)

        layer = QgsProject.instance().mapLayersByName(LAYER_NUMBERING)
        if layer:
            layer = layer[0]
            root = QgsProject.instance().layerTreeRoot()
            node = root.findLayer(layer.id())
            if node:
                node.setItemVisibilityChecked(True)
