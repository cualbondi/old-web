/*
 * Basado en
 *   https://gist.github.com/glenrobertson/3630960
 *   https://github.com/Leaflet/Leaflet/blob/master/src/layer/marker/Marker.js
 * 
 * */

L.EditableCircleMarker = L.Class.extend({
    includes: L.Mixin.Events,
 
    options: {
        weight: 1,
        clickable: false
    },
 
    initialize: function (latlng, radius, options) {
        L.Util.setOptions(this, options);
 
        this._latlng = L.latLng(latlng);
        this._radius = radius;
        this._markerIcon = new L.DivIcon({
            className: this.options.className
        }),
        //console.log(this._markerIcon)
        this._marker = new L.Marker(latlng, {
            icon: this._markerIcon,
            draggable: true
        });
 
        /*
        this._marker = new L.Marker(latlng, {
            draggable: 'true'
        });
        */
        this._circle = new L.Circle(latlng, radius, this.options);
 
        // move circle when marker is dragged
        var self = this;
        this._marker.on('movestart', function() {
            self.fire('movestart');
        });
        this._marker.on('move', function(latlng) {
            var oldLatLng = self._latlng;
            self._latlng = this._latlng;
            self._circle.setLatLng(self._latlng);
            return self.fire('move', { oldLatLng: oldLatLng, latlng: self._latlng });
        });
        this._marker.on('moveend', function() {
            self._marker.setLatLng(this._latlng);
            self.fire('moveend');
        });
    },
 
    onAdd: function (map) {
        this._map = map;
        this._marker.onAdd(map);
        this._circle.onAdd(map);
        this._marker.dragging.enable();
        this.fire('loaded');
    },
 
    onRemove: function (map) {
        this._marker.onRemove(map);
        this._circle.onRemove(map);
        this.fire('unloaded');
    },
 
    getBounds: function() {
        return this._circle.getBounds();
    },
 
    getLatLng: function () {
        return this._latlng;
    },
 
    setLatLng: function (latlng) {
        this._marker.fire('movestart');
        this._latlng = L.latLng(latlng);
        this._marker.setLatLng(this._latlng);
        this._circle.setLatLng(this._latlng);
        this._marker.fire('moveend');
    },
 
    getRadius: function () {
        return this._radius;
    },
 
    setRadius: function (meters) {
        //this._marker.fire('movestart');
        this._radius = meters;
        this._circle.setRadius(meters);
        //this._marker.fire('moveend');
    },
 
    getCircleOptions: function () {
        return this._circle.options;
    },
 
    setCircleStyle: function (style) {
        this._circle.setStyle(style);
    },
 
});
 
L.editableCircleMarker = function (latlng, radius, options) {
    return new L.EditableCircleMarker(latlng, radius, options);
};
