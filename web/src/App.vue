<template>
    <div id="app">
        <router-view/>
    </div>
</template>

<script>
export default {
    name: 'App'
}
</script>

<style>

html, body {
    height: 100%;
    width: 100%;
    overflow: hidden;
    margin: 0;
    padding: 0;
    background: #fff;
}

body {
    color: #333;
    font-family: "PingFang SC", "Helvetica Neue", Helvetica, "Hiragino Sans GB", STHeitiSC-Light, "Microsoft YaHei", "微软雅黑", Arial, sans-serif
}

/* 修复子菜单弹出样式 */
.el-menu--vertical .el-menu--popup {
    max-width: 180px !important;
}

.el-menu--vertical .el-menu-item {
    max-width: 180px !important;
    width: 180px !important;
    min-width: 180px !important;
}
</style>
