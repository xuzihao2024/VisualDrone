import * as Cesium from 'cesium';

export class CreateFrustum {
    constructor(options){
        this.viewer = options.viewer;
        this.position = options.position;
        this.orientation = options.orientation;
        this.fov = options.fov || 30;
        this.near = options.near || 10;
        this.far = options.far || 100;
        this.aspectRatio = options.aspectRatio;
        this.add();
    }

    // 更新视锥体的姿态
    update(position, orientation){
        this.position = position;
        this.orientation = orientation;
        this.add();
    }

    // 创建视锥体和轮廓线
    add(){
        this.clear();
        this.addFrustum();
    }

    // 清除视锥体和轮廓线
    clear(){
        this.clearFrustum();
    }

    // 清除视锥体
    clearFrustum(){
        if(this.frustumPrimitive){
            this.frustumPrimitive.forEach(primitive => {
                this.viewer.scene.primitives.remove(primitive);
            });
            this.frustumPrimitive = null;
        }
    }

    // 创建视锥体及轮廓线
    addFrustum(){
        let frustum = new Cesium.PerspectiveFrustum({
            fov: Cesium.Math.toRadians(this.fov),
            aspectRatio: this.aspectRatio,
            near: this.near,
            far: this.far,
        });
        let instanceGeo = new Cesium.GeometryInstance({
            geometry: new Cesium.FrustumGeometry({
                frustum: frustum,
                origin: this.position,
                orientation: this.orientation,
                vertexFormat: Cesium.VertexFormat.POSITION_ONLY,
            }),
            attributes: {
                color: Cesium.ColorGeometryInstanceAttribute.fromColor(
                    new Cesium.Color(1.0, 0.0, 0.0, 0.1)
                ),
            },
        });
        let instanceGeoLine = new Cesium.GeometryInstance({
            geometry: new Cesium.FrustumOutlineGeometry({
                frustum: frustum,
                origin: this.position,
                orientation: this.orientation,
            }),
            attributes: {
                color: Cesium.ColorGeometryInstanceAttribute.fromColor(
                    new Cesium.Color(1.0, 0.0, 0.0, 0.5)
                ),
            },
        });

        // 使用一个 Primitive 显示填充的视锥体
        let primitiveFill = new Cesium.Primitive({
            geometryInstances: [instanceGeo],
            appearance: new Cesium.PerInstanceColorAppearance({
                closed: true,
                flat: true,
            }),
            asynchronous: false,
        });

        // 使用另外一个 Primitive 显示视锥体的轮廓线
        let primitiveLine = new Cesium.Primitive({
            geometryInstances: [instanceGeoLine],
            appearance: new Cesium.PerInstanceColorAppearance({
                closed: false,
                flat: true,
            }),
            asynchronous: false,
        });

        // 保存这两个 Primitive
        this.frustumPrimitive = [primitiveFill, primitiveLine];
        this.frustumPrimitive.forEach(primitive => {
            this.viewer.scene.primitives.add(primitive);
        });
    }
}
