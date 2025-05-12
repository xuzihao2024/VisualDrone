<!-- https://github.com/xuzihao2024/VisualDrone -->

<template>
  <div id="cesiumContainer" ref="cesiumContainer" v-if="isLoggedIn"></div>
  
  <!-- 登录注册界面 -->
  <div class="auth-overlay" v-if="!isLoggedIn">
    <div class="logo-container">
      <img src="\shulogo.png" alt="University Logo" class="login-logo">
    </div>
    <div class="auth-container">
      <h2>{{ isRegistering ? '用户注册' : '用户登录' }}</h2>
      
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          placeholder="请输入用户名"
        />
      </div>
      
      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          placeholder="请输入密码"
        />
      </div>
      
      <div class="form-group" v-if="isRegistering">
        <label for="confirmPassword">确认密码</label>
        <input 
          type="password" 
          id="confirmPassword" 
          v-model="confirmPassword" 
          placeholder="请再次输入密码"
        />
      </div>
      
      <div class="auth-buttons">
        <button @click="handleSubmit" class="primary-button">
          {{ isRegistering ? '注册' : '登录' }}
        </button>
        <button @click="toggleAuthMode" class="secondary-button">
          {{ isRegistering ? '已有账号？去登录' : '没有账号？去注册' }}
        </button>
      </div>
      
      <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
    </div>
  </div>
  
  <!-- 数据加载前的初始界面 -->
  <div v-if="isLoggedIn && !dataLoaded" class="folder-selection-overlay">
    <div class="folder-selection-container">
      <h2>请选择数据文件夹</h2>
      <p>选择包含以下文件的文件夹:</p>
      <ul>
        <li>full_data.kml</li>
        <li>full_data.csv</li>
        <li>processed_targets.csv</li>
      </ul>
      <div class="file-input-container">
        <input 
          type="file" 
          ref="folderSelector" 
          webkitdirectory 
          directory
          @change="handleFolderSelection" 
          style="display:none"
        />
        <button @click="openFolderDialog" class="folder-button">选择文件夹</button>
      </div>
    </div>
  </div>
  
  <div class="search-container" v-if="isLoggedIn && dataLoaded">
    <div class="user-info">
      <span>{{ username }}</span>
      <button @click="logout" class="logout-button">退出登录</button>
    </div>
    <input 
      type="text" 
      v-model="searchId" 
      placeholder="输入点ID..." 
      @keyup.enter="searchPoint"
    />
    <button @click="searchPoint">查询</button>
    <button @click="resetHighlight">重置</button>
    <button @click="resetDataAndShowSelector" class="folder-button">切换数据文件夹</button>
  </div>
  
  <div v-if="showInfoBox" class="info-box">
    <div class="info-header">
      <h3>点位信息 (ID: {{ pointInfo.id }})</h3>
      <span class="close-btn" @click="closeInfoBox">×</span>
    </div>
    <div class="info-content">
      <p><strong>经度:</strong> {{ pointInfo.longitude }}</p>
      <p><strong>纬度:</strong> {{ pointInfo.latitude }}</p>
      <p><strong>目标类型:</strong> {{ pointInfo.objectClass }}</p>
    </div>
  </div>
</template>

<script setup>
import * as Cesium from 'cesium';
import "./Widgets/widgets.css";
import { onMounted, ref } from 'vue';
import { CreateFrustum } from './CreateFrustum';
import Papa from 'papaparse';

//设置cesium token
Cesium.Ion.defaultAccessToken =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5NjBkZDk1My1kMWMxLTRhNTgtYjYyOC02NGE1NjA2NDkwNDgiLCJpZCI6Mjc2ODg5LCJpYXQiOjE3Mzk4NTk2MzF9.ZZxLsWg6xyB4jpLsNlTmCoa2Vlg36GAt_GBnVwSwlrk";

//静态资源路径
window.CESIUM_BASE_URL = '/';

//设置默认相机视角在中国
Cesium.Camera.DEFAULT_VIEW_RECTANGLE = Cesium.Rectangle.fromDegrees(
  72,
  3,
  136,
  54
);

const searchId = ref('');
const highlightedEntity = ref(null);
// 将viewer定义为组件级变量，而不是只在onMounted中定义
const viewer = ref(null);

const showInfoBox = ref(false);
const pointInfo = ref({});
const dataLoaded = ref(false);

// 登录注册相关状态
const isLoggedIn = ref(false);
const isRegistering = ref(false);
const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const errorMessage = ref('');

function handleSubmit() {
  // 在控制台输出当前输入的值，帮助调试
  console.log('提交的表单数据:', {
    isRegistering: isRegistering.value,
    username: username.value,
    password: password.value,
    confirmPassword: confirmPassword.value
  });

  if (isRegistering.value) {
    if (!username.value.trim() || !password.value.trim() || !confirmPassword.value.trim()) {
      errorMessage.value = '请填写所有字段';
      return;
    }
    if (password.value !== confirmPassword.value) {
      errorMessage.value = '两次输入的密码不一致';
      return;
    }
    // 模拟注册成功
    localStorage.setItem(`user_${username.value}`, password.value);
    alert('注册成功，请登录');
    isRegistering.value = false;
    errorMessage.value = '';
    // 清空输入框，方便用户登录
    password.value = '';
    confirmPassword.value = '';
  } else {
    if (!username.value.trim() || !password.value.trim()) {
      errorMessage.value = '请填写用户名和密码';
      return;
    }
    
    // 模拟登录验证
    const savedPassword = localStorage.getItem(`user_${username.value}`);
    if (savedPassword && savedPassword === password.value) {
      // 登录成功
      isLoggedIn.value = true;
      errorMessage.value = '';
      // 存储登录状态
      localStorage.setItem('currentUser', username.value);
    } else {
      errorMessage.value = '用户名或密码错误';
    }
  }
}

function toggleAuthMode() {
  isRegistering.value = !isRegistering.value;
  errorMessage.value = '';
}

function logout() {
  isLoggedIn.value = false;
  username.value = '';
  password.value = '';
  confirmPassword.value = '';
  errorMessage.value = '';
}

function searchPoint() {
  if (!searchId.value || !viewer.value) return;

  const entities = viewer.value.entities.values;
  const targetEntity = entities.find(entity => 
    entity.label && 
    entity.label.text && 
    typeof entity.label.text._value === 'string' && 
    entity.label.text._value.includes(`ID: ${searchId.value}`)
  );

  if (targetEntity) {
    if (highlightedEntity.value) {
      highlightedEntity.value.point.color = Cesium.Color.RED;
    }
    targetEntity.point.color = Cesium.Color.YELLOW;
    highlightedEntity.value = targetEntity;
    viewer.value.flyTo(targetEntity);

    // 显示信息框
    showInfoBox.value = true;
    
    // 获取点的位置信息（经纬度）
    const position = targetEntity.position._value;
    const cartographic = Cesium.Cartographic.fromCartesian(position);
    const longitudeDegrees = Cesium.Math.toDegrees(cartographic.longitude).toFixed(6);
    const latitudeDegrees = Cesium.Math.toDegrees(cartographic.latitude).toFixed(6);
    const height = cartographic.height > 0 ? cartographic.height.toFixed(2) : null;
    
    // 更新点信息
    pointInfo.value = {
      id: searchId.value,
      longitude: longitudeDegrees,
      latitude: latitudeDegrees,
      altitude: height,
      objectClass: targetEntity.properties?.objectClass?._value || '未知'
    };
  } else {
    alert('未找到对应的点');
  }
}

function resetHighlight() {
  if (highlightedEntity.value) {
    highlightedEntity.value.point.color = Cesium.Color.RED;
    highlightedEntity.value = null;
  }
  showInfoBox.value = false;
}

function closeInfoBox() {
  showInfoBox.value = false;
}

function handleFolderSelection(event) {
  const files = Array.from(event.target.files);
  if (files.length === 0) {
    alert('请选择包含数据文件的文件夹');
    return;
  }
  
  console.log('选择的文件夹包含以下文件:', files.map(f => f.name).join(', '));
  
  // 更灵活地查找所需文件
  const kmlFile = files.find(file => file.name.toLowerCase().endsWith('.kml'));
  const targetsFile = files.find(file => file.name.toLowerCase().includes('target') && file.name.toLowerCase().endsWith('.csv'));
  const flightDataFile = files.find(file => 
    (file.name.toLowerCase().includes('flight') || file.name.toLowerCase().includes('airdata') || file.name.toLowerCase().includes('full_data')) && 
    file.name.toLowerCase().endsWith('.csv')
  );
  
  if (!targetsFile) {
    alert('未找到目标点数据文件（包含target的CSV文件），请选择包含此文件的文件夹');
    return;
  }

  // 确保Cesium地图已初始化
  if (!viewer.value) {
    initCesiumViewer();
  }
  
  // 清除之前的数据
  clearPreviousData();
  
  let loadedFiles = 0;
  let requiredFiles = targetsFile ? 1 : 0;
  requiredFiles += kmlFile ? 1 : 0;
  requiredFiles += flightDataFile ? 1 : 0;
  
  const checkAllFilesLoaded = () => {
    loadedFiles++;
    console.log(`已加载 ${loadedFiles}/${requiredFiles} 个文件`);
    if (loadedFiles >= requiredFiles) {
      console.log('所有数据文件加载完成');
      dataLoaded.value = true;
    }
  };
  
  // 读取并加载点数据
  console.log('开始加载目标点数据...');
  const targetsReader = new FileReader();
  targetsReader.onload = e => {
    console.log('目标点数据读取成功，开始解析...');
    const csvText = e.target.result;
    loadTargetsData(csvText);
    checkAllFilesLoaded();
  };
  targetsReader.onerror = e => {
    console.error('读取目标点数据出错:', e);
    alert('读取目标点数据出错');
  };
  targetsReader.readAsText(targetsFile);
  
  // 如果有KML文件，读取并加载轨迹
  if (kmlFile) {
    console.log('开始加载KML轨迹数据...');
    const kmlReader = new FileReader();
    kmlReader.onload = e => {
      console.log('KML轨迹数据读取成功，开始解析...');
      const kmlText = e.target.result;
      loadKmlData(kmlText);
      checkAllFilesLoaded();
    };
    kmlReader.onerror = e => {
      console.error('读取KML数据出错:', e);
      alert('读取KML数据出错');
      checkAllFilesLoaded();
    };
    kmlReader.readAsText(kmlFile);
  } else {
    console.warn('未找到KML文件，无法加载轨迹数据');
  }
  
  // 如果找到CSV文件，读取并加载视锥体数据
  if (flightDataFile) {
    console.log('开始加载飞行CSV数据...');
    const csvReader = new FileReader();
    csvReader.onload = e => {
      console.log('飞行CSV数据读取成功，开始解析...');
      const csvText = e.target.result;
      loadFrustumData(csvText);
      checkAllFilesLoaded();
    };
    csvReader.onerror = e => {
      console.error('读取飞行数据出错:', e);
      alert('读取飞行数据出错');
      checkAllFilesLoaded();
    };
    csvReader.readAsText(flightDataFile);
  } else {
    console.warn('未找到飞行CSV数据文件，无法加载视锥体数据');
  }
}

function clearPreviousData() {
  // 清除现有的entities
  if (viewer.value) {
    viewer.value.entities.removeAll();
    
    // 清除数据源
    while (viewer.value.dataSources.length > 0) {
      viewer.value.dataSources.remove(viewer.value.dataSources.get(0), true);
    }
    
    // 重置高亮点
    highlightedEntity.value = null;
    showInfoBox.value = false;
  }
}

function loadTargetsData(csvText) {
  Papa.parse(csvText, {
    header: true,
    complete: (results) => {
      // Create a single entity collection for better performance
      const entities = viewer.value.entities;
      
      // Add points for each target
      results.data.forEach(target => {
        if (!target.target_latitude || !target.target_longitude) return;
        
        const latitude = parseFloat(target.target_latitude);
        const longitude = parseFloat(target.target_longitude);
        
        if (isNaN(latitude) || isNaN(longitude)) return;
        
        // Create point entity
        entities.add({
          position: Cesium.Cartesian3.fromDegrees(longitude, latitude),
          point: {
            pixelSize: 8,
            color: Cesium.Color.RED,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2,
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
          },
          label: {
            text: `ID: ${target.track_id}`,
            font: '12px sans-serif',
            pixelOffset: new Cesium.Cartesian2(0, -15),
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            scale: 0.8,
            showBackground: true,
            backgroundColor: new Cesium.Color(0, 0, 0, 0.5),
            horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          },
          // 存储自定义属性
          properties: {
            trackId: target.track_id,
            objectClass: target.obj_class || '未知',
            originalData: target
          }
        });
      });
      
      console.log(`Added ${results.data.length} target points to the map`);
      
      // 缩放到所有点
      viewer.value.zoomTo(viewer.value.entities);
    },
    error: (error) => {
      console.error('Error parsing targets CSV:', error);
      alert('解析目标点数据出错，请选择正确的CSV文件');
    }
  });
}

function loadKmlData(kmlText) {
  // 使用Blob创建一个临时文件对象URL
  const blob = new Blob([kmlText], { type: 'application/vnd.google-earth.kml+xml' });
  const url = URL.createObjectURL(blob);
  
  // 加载KML数据
  Cesium.KmlDataSource.load(url)
    .then((dataSource) => {
      // 清除临时URL
      URL.revokeObjectURL(url);
      
      // 遍历所有 entity，将 billboard 显示设置为 false
      dataSource.entities.values.forEach(entity => {
        if (entity.billboard) {
          entity.billboard.show = false;
        }
      });
      
      viewer.value.dataSources.add(dataSource);
      viewer.value.zoomTo(dataSource);
    })
    .catch(error => {
      console.error('加载KML数据出错:', error);
      alert('加载KML数据出错，请选择正确的KML文件');
    });
}

function loadFrustumData(csvText) {
  Papa.parse(csvText, {
    header: true,
    complete: (results) => {
      let previousDatetime = results.data[0]?.["datetime(utc)"];
      let firstChangedMs = null;
      
      // 遍历数据查找第一次发生变化时的 time(millisecond)
      for (let i = 1; i < results.data.length; i++) {
        const currentDatetime = results.data[i]["datetime(utc)"];
        if (currentDatetime && currentDatetime !== previousDatetime) {
          firstChangedMs = results.data[i]["time(millisecond)"];
          break;
        }
      }
      
      // 如果没有找到datetime列，可能是CSV格式不对
      if (!previousDatetime) {
        console.error('CSV格式不正确，找不到datetime(utc)列');
        alert('CSV格式不正确，无法加载视锥体数据');
        return;
      }
      
      //读取开始时间，保存至字符串
      let startTimeString = results.data[0]["datetime(utc)"];
      // 拆分日期和时间
      let [datePart, timePart] = startTimeString.split(" ");
      let [year, month, day] = datePart.split("-").map(Number);
      let [hour, minute, second] = timePart.split(":").map(Number);
      // 创建 JavaScript Date 对象（注意月份从 0 开始）
      let startDate = new Date(Date.UTC(year, month - 1, day, hour, minute, second));
      // 转换为 Cesium 的 JulianDate
      let startJulianDate = Cesium.JulianDate.fromDate(startDate);
      viewer.value.clock.startTime = startJulianDate;
      viewer.value.clock.currentTime = startJulianDate;
      
      const sampledPosition = new Cesium.SampledPositionProperty();
      const sampledOrientation = new Cesium.SampledProperty(Cesium.Quaternion);
      
      results.data.forEach((row, index) => {
        if (!row["datetime(utc)"]) {
          return;
        }
        
        let [datePart, timePart] = row["datetime(utc)"].split(" ");
        let [year, month, day] = datePart.split("-").map(Number);
        let [hour, minute, second] = timePart.split(":").map(Number);
        let ms = (Number(row["time(millisecond)"]) - firstChangedMs) % 1000;
        let time = new Date(Date.UTC(year, month - 1, day, hour, minute, second, ms));
        let julianTime = Cesium.JulianDate.fromDate(time);
        let longitude = Number(row["longitude"]);
        let latitude = Number(row["latitude"]);
        let altitude = Number(row["altitude_above_seaLevel(feet)"]) * 0.3048;
        let position = Cesium.Cartesian3.fromDegrees(longitude, latitude, altitude);

        let droneHeading = Cesium.Math.toRadians(Number(row[" compass_heading(degrees)"]));
        let dronePitch = Cesium.Math.toRadians(Number(row[" pitch(degrees)"]));
        let droneRoll = Cesium.Math.toRadians(Number(row[" roll(degrees)"]));
        let droneHpr = new Cesium.HeadingPitchRoll(droneHeading, dronePitch, droneRoll);
        let droneQuaternion = Cesium.Transforms.headingPitchRollQuaternion(position, droneHpr);
        sampledPosition.addSample(julianTime, position);
        sampledOrientation.addSample(julianTime, droneQuaternion);
      });
      
      // 创建无人机实体
      const droneEntity = viewer.value.entities.add({
        position: sampledPosition,
        orientation: sampledOrientation,
        model: {
          uri: '/models/drone.glb',
          minimumPixelSize: 32,
          maximumScale: 0.3,
          runAnimations: false,
          scale: 0.3
        }
      });
      
      // 设置视锥体
      let origin = Cesium.Cartesian3.fromDegrees(
        Number(results.data[0]["longitude"]), 
        Number(results.data[0]["latitude"]), 
        Number(results.data[0]["altitude_above_seaLevel(feet)"]) * 0.3048
      );
      let heading = Cesium.Math.toRadians(0);
      let pitch = Cesium.Math.toRadians(0);
      let roll = Cesium.Math.toRadians(0);
      let hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
      let orientation = Cesium.Quaternion.fromHeadingPitchRoll(hpr);
      
      let createFrustum = new CreateFrustum({
        viewer: viewer.value,
        position: origin,
        orientation: orientation,
        fov: 35,
        near: 3,
        far: 100,
        aspectRatio: 320/568,
      });
      
      // 使用 viewer.clock.onTick 来动态更新视锥体
      viewer.value.clock.onTick.addEventListener((clock) => {
        let elapsedSeconds = Cesium.JulianDate.secondsDifference(clock.currentTime, clock.startTime);
        let i = Math.floor(elapsedSeconds / 0.1);
        // 当索引超过数据长度时停止更新，避免报错
        if (i < results.data.length - 1 && i >= 0) {
          origin = Cesium.Cartesian3.fromDegrees(
            Number(results.data[i]["longitude"]), 
            Number(results.data[i]["latitude"]), 
            Number(results.data[i]["altitude_above_seaLevel(feet)"]) * 0.3048
          );
          heading = Cesium.Math.toRadians(Number(results.data[i]["gimbal_heading(degrees)"]));
          pitch = Cesium.Math.toRadians(90-Number(results.data[i]["gimbal_pitch(degrees)"]));
          roll = Cesium.Math.toRadians(Number(results.data[i]["gimbal_roll(degrees)"]));
          hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
          orientation = Cesium.Transforms.headingPitchRollQuaternion(origin, hpr);
          createFrustum.update(origin, orientation);
        }
      });
      
      console.log('视锥体数据加载完成');
    },
    error: (error) => {
      console.error('解析 CSV 数据出错：', error);
      alert('解析CSV数据出错，无法加载视锥体数据');
    }
  });
}

function openFolderDialog() {
  // 获取文件输入元素并触发点击
  const folderSelector = document.querySelector('input[type="file"][webkitdirectory]');
  if (folderSelector) {
    folderSelector.click();
  }
}

function resetDataAndShowSelector() {
  // 清除现有数据
  clearPreviousData();
  // 显示文件夹选择界面
  dataLoaded.value = false;
}

function initCesiumViewer() {
  viewer.value = new Cesium.Viewer('cesiumContainer', {
    //信息窗口
    infoBox: false,
    //地图模式
    sceneModePicker: false,
    //地图图层
    baseLayerPicker: false,
    //帮助按钮
    navigationHelpButton: false,
  });
  //隐藏logo
  viewer.value.cesiumWidget.creditContainer.style.display = "none";
}

onMounted(() => {
  initCesiumViewer();
  
  // 默认显示文件夹选择界面，不加载任何数据
  dataLoaded.value = false;
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
}

#cesiumContainer {
  width: 100vw;
  height: 100vh;
}

.top-controls {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.8);
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
}

.folder-selector {
  margin-bottom: 10px;
}

.folder-selector label {
  margin-right: 5px;
}

.folder-selector select {
  padding: 5px;
}

.search-container {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(30, 30, 30, 0.75);
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.search-container .user-info {
  margin-right: 15px;
  color: #e0e0e0;
  display: flex;
  align-items: center;
}

.search-container input {
  margin-right: 5px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  color: #fff;
}

.search-container button {
  padding: 8px 12px;
  margin: 0 5px;
  background: rgba(0, 123, 255, 0.7);
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-container button:hover {
  background: rgba(0, 123, 255, 0.9);
}

.folder-button {
  background: rgba(73, 80, 87, 0.7) !important;
}

.folder-button:hover {
  background: rgba(73, 80, 87, 0.9) !important;
}

.logout-button {
  padding: 6px 12px;
  background: rgba(220, 53, 69, 0.7) !important;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.2s;
  margin-left: 5px;
}

.logout-button:hover {
  background: rgba(220, 53, 69, 0.9) !important;
}

.info-box {
  position: absolute;
  top: 70px;
  left: 10px;
  background: rgba(30, 30, 30, 0.85);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  width: 300px;
  color: #fff;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 10px;
}

.info-header h3 {
  margin: 0;
  font-size: 16px;
  color: #fff;
}

.close-btn {
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.8);
  transition: color 0.2s;
}

.close-btn:hover {
  color: #fff;
}

.info-content p {
  margin: 10px 0;
  color: #e0e0e0;
}

.info-content strong {
  color: #fff;
  margin-right: 6px;
}

.folder-selection-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
}

.folder-selection-container {
  background: rgba(30, 30, 30, 0.85);
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  width: 400px;
  max-width: 90%;
  color: #fff;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.folder-selection-container h2 {
  margin-bottom: 20px;
  font-size: 22px;
  text-align: center;
  color: #fff;
}

.folder-selection-container p {
  color: #e0e0e0;
  margin-bottom: 15px;
}

.folder-selection-container ul {
  margin-bottom: 20px;
  color: #e0e0e0;
  list-style-position: inside;
}

.folder-selection-container li {
  margin-bottom: 8px;
  opacity: 0.9;
}

.file-input-container {
  text-align: center;
  margin-top: 25px;
}

.folder-button {
  padding: 12px 25px;
  background: rgba(0, 123, 255, 0.8);
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 15px;
}

.folder-button:hover {
  background: rgba(0, 123, 255, 1);
}

.auth-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: white;
  display: flex;
  flex-direction: column; /* 纵向排列 */
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.logo-container {
  text-align: center;
  margin-bottom: 20px;
  margin-top: 0;
  /* 保证 logo 在登录框上方居中 */
}

.login-logo {
  max-width: 150px;
  height: auto;
  display: inline-block;
}

.auth-container {
  background: rgba(30, 30, 30, 0.85);
  padding: 25px 40px; /* 增加左右内边距 */
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  width: 320px; /* 稍微缩小宽度 */
  max-width: 90%;
  color: #fff;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin: 0 auto; /* 确保容器居中 */
}

.auth-container h2 {
  margin-bottom: 20px;
  font-size: 22px;
  text-align: center;
  color: #fff;
}

.form-group {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  align-items: center; /* 使内容居中对齐 */
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #e0e0e0;
  align-self: flex-start; /* 标签左对齐 */
  width: 100%; /* 让标签占满宽度 */
}

.form-group input {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  color: #fff;
  font-size: 14px;
  box-sizing: border-box; /* 确保内边距不会增加元素实际宽度 */
}

.form-group input:focus {
  outline: none;
  border-color: rgba(0, 123, 255, 0.5);
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.auth-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 25px;
}

.primary-button {
  padding: 10px 20px;
  background: rgba(0, 123, 255, 0.8);
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.primary-button:hover {
  background: rgba(0, 123, 255, 1);
}

.secondary-button {
  padding: 10px 20px;
  background: rgba(108, 117, 125, 0.5);
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.secondary-button:hover {
  background: rgba(108, 117, 125, 0.8);
}

.error-message {
  color: #ff6b6b;
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
}
</style>
