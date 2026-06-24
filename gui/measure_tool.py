"""Map measure tool for distance measurement on canvas."""

from typing import Any

from qgis.core import QgsDistanceArea, QgsPointXY, QgsWkbTypes
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsVertexMarker
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QCursor, QFont
from qgis.PyQt.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsItemGroup,
    QGraphicsSimpleTextItem,
    QGraphicsTextItem,
    QToolTip,
)

from ..constants import current_locale
from ..i18n import tr as _i18n_tr


class MeasureTool(QgsMapToolEmitPoint):
    """Map tool for measuring distances on the canvas."""

    def __init__(self, canvas, iface) -> None:
        """Initialize the measurement tool with canvas and interface."""
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface
        self.points: list[QgsPointXY] = []
        self.da = QgsDistanceArea()
        self.da.setEllipsoid('WGS84')

        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0, 180))
        self.rubber_band.setWidth(2)

        self.markers: list[QgsVertexMarker] = []
        self.labels: list[QGraphicsItemGroup] = []
        self.paused = False

        # Connect to both signals to ensure labels update on any canvas change
        self.canvas.extentsChanged.connect(self.updateLabels)
        self.canvas.scaleChanged.connect(self.updateLabels)

    def canvasReleaseEvent(self, event: Any) -> None:
        """Record point and draw measurement lines."""
        if self.paused:
            return

        point = self.toMapCoordinates(event.pos())
        self.points.append(point)

        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        marker.setColor(QColor(255, 0, 0))
        marker.setIconType(QgsVertexMarker.ICON_CROSS)
        marker.setIconSize(12)
        marker.setPenWidth(2)
        self.markers.append(marker)

        if len(self.points) == 1:
            self.rubber_band.reset(QgsWkbTypes.LineGeometry)
            self.rubber_band.addPoint(point, False)
        else:
            self.rubber_band.addPoint(point, True)
            self.rubber_band.show()

            # Add distance label between last two points
            self.addDistanceLabel(self.points[-2], self.points[-1])

            # Show total distance
            total_dist = sum(
                self.da.measureLine(self.points[i - 1], self.points[i])
                for i in range(1, len(self.points))
            )
            msg = f'{total_dist:.2f} {_i18n_tr("m", current_locale())}'
            self.iface.messageBar().pushMessage(
                _i18n_tr('Total Distance', current_locale()), msg, level=0, duration=10
            )

    def canvasMoveEvent(self, event: Any) -> None:
        """Show temporary distance on mouse move."""
        if self.paused or not self.points:
            return

        current_point = self.toMapCoordinates(event.pos())
        self.rubber_band.removeLastPoint()
        self.rubber_band.addPoint(current_point, True)

        temp_distance = self.da.measureLine(self.points[-1], current_point)
        total_dist = sum(
            self.da.measureLine(self.points[i - 1], self.points[i])
            for i in range(1, len(self.points))
        )
        dist_msg = f'{temp_distance + total_dist:.2f} {_i18n_tr("m", current_locale())}'
        QToolTip.showText(QCursor.pos(), dist_msg)

    def keyPressEvent(self, event: Any) -> None:
        """Handle keyboard shortcuts for tool control."""
        if event.key() == Qt.Key.Key_R:
            self.clear()
            self.iface.messageBar().pushMessage(
                _i18n_tr('Update', current_locale()),
                _i18n_tr('Restart Measurement', current_locale()),
                level=1,
                duration=10,
            )

        elif event.key() == Qt.Key.Key_E:
            self.clear()
            self.canvas.unsetMapTool(self)
            self.iface.messageBar().pushMessage(
                _i18n_tr('Finish', current_locale()),
                _i18n_tr('Measurement tool terminated', current_locale()),
                level=0,
                duration=10,
            )

        elif event.key() == Qt.Key.Key_P:
            self.paused = not self.paused
            state = (
                _i18n_tr('Paused', current_locale())
                if self.paused
                else _i18n_tr('Resumed', current_locale())
            )
            level = 1 if self.paused else 0
            self.iface.messageBar().pushMessage(
                _i18n_tr('Status', current_locale()), state, level=level, duration=10
            )

    def addDistanceLabel(self, point1: Any, point2: Any) -> None:
        """Add a distance label between two points on canvas."""
        mid_x = (point1.x() + point2.x()) / 2
        mid_y = (point1.y() + point2.y()) / 2
        mid_point = QgsPointXY(mid_x, mid_y)

        segment_distance = self.da.measureLine(point1, point2)
        total_distance = sum(
            self.da.measureLine(self.points[i - 1], self.points[i])
            for i in range(1, len(self.points))
        )

        rle = '\u202b'
        pdf = '\u202c'

        label_text = (
            f' {rle}{segment_distance:.2f} {_i18n_tr("m", current_locale())}\n'
            f' {total_distance:.2f} {_i18n_tr("m", current_locale())}{pdf} '
        )

        # Create a group to hold the text with outline effect
        group = QGraphicsItemGroup()
        group.mid_point = mid_point

        font = QFont('Arial', 11)
        text_item = QGraphicsSimpleTextItem(label_text)
        text_item.setFont(font)
        text_rect = text_item.boundingRect()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setOffset(0)
        shadow.setColor(QColor(255, 255, 255))
        text_item.setGraphicsEffect(shadow)
        text_item.setBrush(QColor(255, 0, 0))
        group.addToGroup(text_item)

        # Position the group at the correct screen coordinates
        screen_pos = self.canvas.getCoordinateTransform().transform(mid_point)
        group.setPos(
            screen_pos.x() - text_rect.width() / 2,
            screen_pos.y() - text_rect.height() / 2,
        )
        group.setZValue(1000)  # Ensure labels stay on top

        self.canvas.scene().addItem(group)
        self.labels.append(group)

    def updateLabels(self) -> None:
        """Update position and optionally font size of labels on zoom/pan."""
        transform = self.canvas.getCoordinateTransform()

        for label in self.labels:
            if hasattr(label, 'mid_point'):
                # Convert map coordinates to screen coordinates
                screen_pos = transform.transform(label.mid_point)

                # Center the label on the point
                if isinstance(label, QGraphicsItemGroup):
                    # For QGraphicsItemGroup, adjust for the text size
                    for item in label.childItems():
                        if isinstance(item, QGraphicsSimpleTextItem):
                            text_rect = item.boundingRect()
                            label.setPos(
                                screen_pos.x() - text_rect.width() / 2,
                                screen_pos.y() - text_rect.height() / 2,
                            )
                            break
                else:
                    label.setPos(screen_pos.x(), screen_pos.y())

                # Optional: Adjust font size based on scale
                current_scale = self.canvas.scale()
                font_size = max(8, min(14, int(10000 / current_scale)))
                for item in label.childItems():
                    if isinstance(item, (QGraphicsSimpleTextItem, QGraphicsTextItem)):
                        font = item.font()
                        font.setPointSize(font_size)
                        item.setFont(font)

    def clear(self) -> None:
        """Clear all markers, labels, and reset the measurement."""
        # Disconnect signals first to avoid duplicate updates
        try:
            self.canvas.extentsChanged.disconnect(self.updateLabels)
            self.canvas.scaleChanged.disconnect(self.updateLabels)
        except TypeError:
            pass

        self.rubber_band.reset(QgsWkbTypes.LineGeometry)
        for marker in self.markers:
            self.canvas.scene().removeItem(marker)
        self.markers.clear()

        for label in self.labels:
            self.canvas.scene().removeItem(label)
        self.labels.clear()

        self.points.clear()
        QToolTip.hideText()

        # Reconnect signals if you plan to continue using the tool
        self.canvas.extentsChanged.connect(self.updateLabels)
        self.canvas.scaleChanged.connect(self.updateLabels)

    def unset_map_tool(self) -> None:
        """Clear measurements and unset the measure tool from canvas."""
        self.clear()
        self.canvas.unsetMapTool(self)
