"""Symbol and layout export mixin for SVG, PNG map generation."""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

import logging

from qgis.core import (
    QgsApplication,
    QgsBasicNumericFormat,
    QgsFillSymbol,
    QgsLayout,
    QgsLayoutExporter,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemPage,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendStyle,
    QgsPrintLayout,
    QgsProject,
    QgsScaleBarSettings,
    QgsTextFormat,
    QgsUnitTypes,
)
from qgis.PyQt.QtCore import QRectF, Qt
from qgis.PyQt.QtGui import QColor, QFont

from ..constants import (
    LAYER_MUNICIPALITY,
    LAYER_NAMES,
    NORTH_ARROW_SVG,
    SCALE_BAR_SVG,
    SITUATION_PNG,
    SYMBOLS_SVG,
)
from ._protocols import (
    HasIface,
    HasScaleContext,
    HasSymbolMapContext,
    HasSymbolPlanContext,
)

logger = logging.getLogger(__name__)


class SymbolExportMixin:
    """Mixin for exporting map layouts (legend, north arrow, scale bar)
    to SVG/PNG."""

    @staticmethod
    def _build_legend(layout, map_item):
        """Create a legend item with styled text formats."""
        legend = QgsLayoutItemLegend(layout)
        legend.setLinkedMap(map_item)
        legend.setAutoUpdateModel(False)
        legend.setSymbolWidth(15)
        legend.setSymbolHeight(10)
        legend.setColumnCount(2)
        legend.setSplitLayer(True)
        legend.setEqualColumnWidth(True)

        text_format = QgsTextFormat()
        text_format.setSize(14)
        text_format.setColor(QColor(0, 0, 0))
        font = QFont()
        font.setBold(True)
        font.setPointSize(30)
        font.setUnderline(True)
        text_format.setFont(font)

        for style in [QgsLegendStyle.Group, QgsLegendStyle.Subgroup]:
            s = legend.style(style)
            s.setTextFormat(text_format)
            s.setMargin(QgsLegendStyle.Top, 4)
            s.setMargin(QgsLegendStyle.Bottom, 4)
            s.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            legend.setStyle(style, s)

        symbol_style = legend.style(QgsLegendStyle.Symbol)
        symbol_style.setMargin(QgsLegendStyle.Top, 3)
        symbol_style.setMargin(QgsLegendStyle.Bottom, 3)
        legend.setStyle(QgsLegendStyle.Symbol, symbol_style)

        layout.addLayoutItem(legend)
        return legend

    @staticmethod
    def _populate_legend_model(legend, layers_to_hide):
        """Populate legend with visible desired layers."""
        legend_model = legend.model()
        root = legend_model.rootGroup()
        root.removeAllChildren()

        for layer_name in LAYER_NAMES:
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name() == layer_name and layer.name() not in layers_to_hide:
                    root.addLayer(layer)
                    break

        legend.setLegendFilterByMapEnabled(False)
        legend.adjustBoxSize()

    @staticmethod
    def _adjust_page_size(layout, map_item, legend):
        """Resize page to fit map and legend."""
        map_rect = map_item.sceneBoundingRect()
        legend_rect = legend.sceneBoundingRect()

        total_width = max(map_rect.right(), legend_rect.right()) + 20
        total_height = max(map_rect.bottom(), legend_rect.bottom()) + 20

        page = layout.pageCollection().pages()[0]
        page.setPageSize(
            QgsLayoutSize(
                total_width,
                total_height,
                QgsUnitTypes.LayoutMillimeters,
            ),
        )

        if legend_rect.height() < total_height - 40:
            new_y = (total_height - legend_rect.height()) / 2
            legend.setPos(legend.scenePos().x(), new_y)

    def symbols(self: HasSymbolPlanContext) -> str | None:
        """Export a layout with map and legend to SVG."""
        if not (self.type_plan and self.type_to_hide):
            return None

        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()

        layers_to_hide = [self.sat_view, self.rast, self.type_to_hide]
        visible_layers = [
            layer
            for layer in project.mapLayers().values()
            if layer.name() not in layers_to_hide
        ]

        map_item = QgsLayoutItemMap(layout)
        map_item.setLayers(visible_layers)
        map_item.attemptSetSceneRect(QRectF(20, 20, 200, 350))
        layout.addLayoutItem(map_item)

        legend = self._build_legend(layout, map_item)
        self._populate_legend_model(legend, layers_to_hide)
        self._adjust_page_size(layout, map_item, legend)

        output_path = SYMBOLS_SVG
        exporter = QgsLayoutExporter(layout)
        svg_settings = QgsLayoutExporter.SvgExportSettings()
        svg_settings.forceVectorOutput = True
        svg_settings.dpi = 900

        result = exporter.exportToSvg(output_path, svg_settings)

        if result == QgsLayoutExporter.Success:
            logger.info(
                'SVG exported with dynamic page size: %s',
                output_path,
            )
            return output_path
        logger.error('Export failed!')
        return None

    def map_situation(self: HasSymbolMapContext) -> None:
        """Export a situation map highlighting the municipality to PNG."""
        project = QgsProject.instance()

        municipality_layer = QgsProject.instance().mapLayersByName(LAYER_MUNICIPALITY)[
            0
        ]

        base_layer = None
        if self.sat_view:
            base_layer = QgsProject.instance().mapLayersByName(self.sat_view)[0]
        elif self.rast:
            base_layer = QgsProject.instance().mapLayersByName(self.rast)[0]

        if base_layer is None:
            logger.warning(
                'No base map layer (satellite or raster) available for situation map'
            )
            return

        red_symbol = QgsFillSymbol.createSimple(
            {'color': '255,0,0,100', 'outline_color': '255,0,0', 'outline_width': '0.6'}
        )

        cloned_renderer = municipality_layer.renderer().clone()
        cloned_renderer.setSymbol(red_symbol)

        municipality_copy = municipality_layer.clone()
        municipality_copy.setRenderer(cloned_renderer)

        layout = QgsLayout(project)
        layout.initializeDefaults()

        page = layout.pageCollection().pages()[0]
        page.setPageSize(
            QgsLayoutSize(257, 170, QgsUnitTypes.LayoutMillimeters),
        )

        map_item = QgsLayoutItemMap(layout)
        map_item.setRect(20, 20, 257, 170)
        map_item.setExtent(municipality_layer.extent())
        map_item.setScale(150000)
        map_item.setLayers([base_layer, municipality_copy])

        layout.addLayoutItem(map_item)

        exporter = QgsLayoutExporter(layout)
        settings = QgsLayoutExporter.ImageExportSettings()
        output_path = SITUATION_PNG
        exporter.exportToImage(output_path, settings)

        logger.info('Map exported to %s', output_path)

    def north(self: HasIface) -> None:
        """Export a north arrow SVG aligned with the current map rotation."""
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName('NorthArrowLayout')

        page = QgsLayoutItemPage(layout)
        page.setPageSize(QgsLayoutSize(50, 50, QgsUnitTypes.LayoutMillimeters))

        layout.pageCollection().addPage(page)

        north_arrow = QgsLayoutItemPicture(layout)
        north_arrow.setPicturePath(
            QgsApplication.svgPaths()[0] + '/arrows/NorthArrow_11.svg',
        )
        north_arrow.attemptResize(
            QgsLayoutSize(40, 40, QgsUnitTypes.LayoutMillimeters),
        )
        north_arrow.attemptMove(
            QgsLayoutPoint(25, 25, QgsUnitTypes.LayoutMillimeters),
        )
        north_arrow.setPictureAnchor(QgsLayoutItemPicture.Middle)
        north_arrow.setResizeMode(QgsLayoutItemPicture.Zoom)

        layout.addLayoutItem(north_arrow)

        map_canvas = self.iface.mapCanvas()
        map_rotation = map_canvas.rotation()

        north_arrow.setRotation(map_rotation)

        export_settings = QgsLayoutExporter.SvgExportSettings()
        export_settings.dpi = 300
        export_settings.cropToContents = True

        exporter = QgsLayoutExporter(layout)
        output_path = NORTH_ARROW_SVG
        exporter.exportToSvg(output_path, export_settings)

    def scale(self: HasScaleContext) -> None:
        """Export a scale bar SVG matching the current map canvas scale."""
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName('ScaleBarLayout')

        page = QgsLayoutItemPage(layout)
        page.setPageSize(QgsLayoutSize(1, 1, QgsUnitTypes.LayoutMillimeters))
        layout.pageCollection().addPage(page)

        map_item = QgsLayoutItemMap(layout)
        map_item.setRect(QRectF(10, 10, 80, 80))
        map_item.zoomToExtent(self.iface.mapCanvas().extent())
        layout.addLayoutItem(map_item)

        map_settings = self.iface.mapCanvas().mapSettings()
        scale_val = map_settings.scale()
        bar_length_mm = 100
        meters_per_mm = scale_val / 1000.0
        total_length_m = meters_per_mm * bar_length_mm

        scale_bar = QgsLayoutItemScaleBar(layout)
        scale_bar.setLinkedMap(map_item)
        scale_bar.setStyle('Double Box')
        scale_bar.setFont(QFont('Arial', 12))
        scale_bar.attemptMove(
            QgsLayoutPoint(10, 85, QgsUnitTypes.LayoutMillimeters),
        )

        if total_length_m >= 1000:
            scale_bar.setUnits(QgsUnitTypes.DistanceKilometers)
            scale_bar.setUnitsPerSegment(0.1)
            scale_bar.setUnitLabel(self._tr('km'))
        else:
            scale_bar.setUnits(QgsUnitTypes.DistanceMeters)
            scale_bar.setUnitsPerSegment(100)
            scale_bar.setUnitLabel(self._tr('m'))

        scale_bar.setNumberOfSegments(2)
        scale_bar.setNumberOfSegmentsLeft(0)
        scale_bar.setSegmentSizeMode(QgsScaleBarSettings.SegmentSizeFitWidth)

        numeric_format = QgsBasicNumericFormat()
        numeric_format.setShowTrailingZeros(False)
        numeric_format.setNumberDecimalPlaces(0)
        scale_bar.setNumericFormat(numeric_format)

        layout.addLayoutItem(scale_bar)

        page.setBackgroundColor(QColor(0, 0, 0, 0))

        export_settings = QgsLayoutExporter.SvgExportSettings()
        export_settings.dpi = 900
        export_settings.cropToContents = True
        export_settings.transparentBackground = True

        output_path = SCALE_BAR_SVG
        exporter = QgsLayoutExporter(layout)
        exporter.exportToSvg(output_path, export_settings)
