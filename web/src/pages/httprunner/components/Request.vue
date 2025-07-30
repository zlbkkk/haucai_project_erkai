<template>
    <div>
        <div style="margin-left: 200px;">
            <el-radio-group v-model="dataType">
                <el-radio
                    v-for="item of dataOptions"
                    :label="item.label"
                    :key="item.value"
                >{{ item.value }}
                </el-radio>
            </el-radio-group>
        </div>
        <div>
            <el-dialog title="批量编辑，每个参数占一行，冒号分隔；Key自动去重" :visible.sync="showDialog">
                <el-input type="textarea" v-model="textareaData" :autosize="{ minRows: 10, maxRows: 16}"
                          class="el-textarea__inner"></el-input>
                <span slot="footer" class="dialog-footer">
        <el-button @click="showDialog = false">取 消</el-button>
        <el-button type="primary" @click="handleSubmit">确 定</el-button>
      </span>
            </el-dialog>
        </div>
        <div style="margin-top: 5px">
            <el-table
                highlight-current-row
                :cell-style="{paddingTop: '4px', paddingBottom: '4px'}"
                strpe
                :height="height"
                :data="dataType === 'data' ? formData: paramsData"
                style="width: 100%;"
                @cell-mouse-enter="cellMouseEnter"
                @cell-mouse-leave="cellMouseLeave"
                v-show="dataType !== 'json' "
            >
                <!--Request params-->
                <el-table-column
                    label="请求Key"
                    width="250">
                    <template slot-scope="scope">
                        <el-input clearable v-model="scope.row.key" placeholder="Key"></el-input>
                    </template>
                </el-table-column>
                <!--Request 表单-->
                <el-table-column
                    v-if="dataType === 'data' "
                    label="类型"
                    width="120">
                    <template slot-scope="scope">
                        <el-select v-model="scope.row.type">
                            <el-option
                                v-for="item in dataTypeOptions"
                                :key="item.value"
                                :label="item.label"
                                :value="item.value"
                            >
                            </el-option>
                        </el-select>

                    </template>
                </el-table-column>

                <el-table-column
                    label="请求Value"
                    width="350">
                    <template slot-scope="scope">
                        <el-input
                            v-show="scope.row.type !== 5"
                            clearable
                            v-model="scope.row.value"
                            placeholder="Value"
                        ></el-input>

                        <el-row v-show="scope.row.type === 5">
                            <el-col :span="7">
                                <el-upload
                                    :key="`upload-${scope.$index}-${scope.row.value}`"
                                    :show-file-list="false"
                                    :action="uploadFile(scope.row)"
                                    :limit="1"
                                    type="small"
                                    :file-list="fileList"
                                    :on-error="uploadError"
                                    :on-success="uploadSuccess"
                                    :headers="{
                                        'Authorization': authToken
                                    }"
                                    :data="{
                                        project: currentProjectId,
                                        description: scope.row.desc || '',
                                        api: currentProjectId
                                    }"
                                >
                                    <el-button
                                        size="small"
                                        type="primary"
                                        @click="currentIndex=scope.$index"
                                    >选择文件
                                    </el-button>
                                </el-upload>
                            </el-col>

                            <el-col :span="12">
                                <div style="margin-top: 8px; display: flex; align-items: center;">
                                    <i class="el-icon-document" v-text="scope.row.value" style="flex: 1;"></i>
                                    <el-button 
                                        v-if="scope.row.value"
                                        type="text" 
                                        icon="el-icon-close" 
                                        size="mini"
                                        @click="clearFile(scope.$index)"
                                        style="margin-left: 5px; color: #f56c6c;"
                                        title="删除文件">
                                    </el-button>
                                </div>
                            </el-col>
                        </el-row>
                    </template>
                </el-table-column>

                <el-table-column
                    label="描述"
                    width="400">
                    <template slot-scope="scope">
                        <el-input clearable v-model="scope.row.desc" placeholder="参数简要描述"></el-input>
                    </template>
                </el-table-column>

                <el-table-column>
                    <template slot="header">
                        <el-button type="info"
                                   size="small"
                                   icon="el-icon-edit"
                                   @click="handleBulkEdit">
                            批量编辑
                        </el-button>

                    </template>
                    <template slot-scope="scope">
                        <el-row v-show="scope.row === currentRow">
                            <el-button
                                icon="el-icon-circle-plus-outline"
                                size="mini"
                                type="info"
                                @click="handleEdit(scope.$index, scope.row)">
                            </el-button>
                            <el-button
                                icon="el-icon-document-copy"
                                size="mini"
                                type="info"
                                @click="handleCopy(scope.$index, scope.row)">
                            </el-button>
                            <el-button
                                icon="el-icon-delete"
                                size="mini"
                                type="danger"
                                v-show="scope.$index !== 0"
                                @click="handleDelete(scope.$index, scope.row)">
                            </el-button>
                        </el-row>

                    </template>
                </el-table-column>
            </el-table>

            <v-jsoneditor v-model="editorJsonData"
                          v-show="dataType === 'json'"
                          :height="height"
                          :options="options" :plus="true"
                          ref="requestEditor"
            >
            </v-jsoneditor>

        </div>

    </div>


</template>

<script>
import VJsoneditor from 'v-jsoneditor'

import bus from '../../../util/bus.js'
import * as api from '../../../restful/api'

export default {
    components: {
        VJsoneditor
    },
    props: {
        save: Boolean,
        request: {
            require: false
        },
        project: {
            type: [Number, String],
            default: function() {
                return this.$route.params.id;
            }
        }
    },
    data() {
        let self = this
        return {
            options: {
                onModeChange(newMode, oldMode) {
                    if (newMode === 'tree') {
                        self.$refs.requestEditor.editor.expandAll()
                    }
                },
                onEvent: function (node, event) {
                    if (event.type === 'click' && event.altKey) {
                        // 左键点击 + alt 提取请求参数jsonpath插入到extract
                        let arr = node.path
                        arr.unshift("request.body")
                        let jsonPath = arr.join(".")
                        self.notifyCopyRequest(jsonPath, 'Extract插入')
                        const extractOjb = {
                            "key": arr[arr.length - 1],
                            "value": jsonPath,
                            "desc": "自动插入"
                        }
                        bus.$emit('extract', extractOjb)
                    }
                    if (event.type === 'click' && event.ctrlKey) {
                        // 左键点击 + ctrl 提取请求参数jsonpath插入到validate
                        let arr = node.path
                        arr.unshift("request.body")
                        let jsonPath = arr.join(".")
                        self.notifyCopyRequest(jsonPath, 'Validate插入')
                        const validateObj = {
                            "expect": node.value,
                            "actual": jsonPath,
                            "comparator": "equals",
                            "type": 1
                        }
                        bus.$emit('validate', validateObj)
                    }
                },
                mode: 'code',
                modes: ['code', 'tree'], // allowed modes
            },
            showDialog: false,
            editorJsonData: {},
            fileList: [],
            currentIndex: 0,
            currentRow: '',
            formData: [{
                key: '',
                value: '',
                type: 1,
                desc: ''
            }],
            paramsData: [{
                key: '',
                value: '',
                type: 1,
                desc: ''
            }],

            dataTypeOptions: [{
                label: 'String',
                value: 1
            }, {
                label: 'Integer',
                value: 2
            }, {
                label: 'Float',
                value: 3
            }, {
                label: 'Boolean',
                value: 4
            }, {
                label: 'File',
                value: 5
            }],

            dataOptions: [{
                label: 'data',
                value: '表单',
            }, {
                label: 'json',
                value: 'json',
            }, {
                label: 'params',
                value: 'params'
            }],
            dataType: 'data',
            timeStamp: "",
            textareaData: "",
            projectId: this.project || this.$route.params.id,
        }
    },

    computed: {
        height() {
            return (window.screen.height - 464).toString() + "px"
        },
        authToken() {
            return this.$store && this.$store.state ? this.$store.state.token : '';
        },
        currentProjectId() {
            return this.projectId || (this.$route && this.$route.params ? this.$route.params.id : null);
        }
    },

    mounted() {
        this.editorJsonData = this.parseJson()
        
        // 只在没有任何数据时才初始化空行
        // 让request watch处理数据加载，避免重复初始化
    },
    name: "Request",

    watch: {
        save: function () {
            // Save SaveAs Send都会触发
            this.$emit('request', {
                form: this.parseForm(),
                json: this.editorJsonData,
                params: this.parseParams(),
                files: this.parseFile()
            }, {
                // 编辑用例步骤用到
                data: this.formData,
                params: this.paramsData,
                json_data: this.editorJsonData
            });
        },

        request: function () {
            if (this.request && Object.keys(this.request).length !== 0) {
                // 处理表单数据
                if (this.request.data && Array.isArray(this.request.data) && this.request.data.length > 0) {
                    this.formData = this.request.data;
                } else {
                    this.formData = [{ key: '', value: '', type: 1, desc: '' }];
                }
                
                // 确保表单数据中的类型正确设置
                if (this.formData && this.formData.length > 0) {
                    this.formData.forEach(item => {
                        if (!item.type) {
                            item.type = 1; // 默认为String类型
                        }
                    });
                    
                    // 检查是否有文件类型的数据，如果有则切换到表单模式
                    const hasFileType = this.formData.some(item => item.type === 5 && item.key !== '');
                    if (hasFileType) {
                        this.dataType = 'data';
                    }
                }
                
                this.editorJsonData = this.parseJson();
                
                // 处理params数据
                if (this.request.params && Array.isArray(this.request.params) && this.request.params.length > 0) {
                    this.paramsData = this.request.params;
                } else {
                    this.paramsData = [{ key: '', value: '', type: 1, desc: '' }];
                }
                
                // 确保params数据中的类型也正确设置
                if (this.paramsData && this.paramsData.length > 0) {
                    this.paramsData.forEach(item => {
                        if (!item.type) {
                            item.type = 1; // 默认为String类型
                        }
                    });
                }
            } else {
                // 如果没有request数据，初始化空行
                if (!this.formData || this.formData.length === 0) {
                    this.formData = [{ key: '', value: '', type: 1, desc: '' }];
                }
                if (!this.paramsData || this.paramsData.length === 0) {
                    this.paramsData = [{ key: '', value: '', type: 1, desc: '' }];
                }
            }
        },
        project: function(newVal) {
            this.projectId = newVal || this.$route.params.id;
        }
    },
    methods: {
        handleSubmit() {
            this.showDialog = false
            const data = this.textareaData.split("\n").map(item => {
                const [key, value, type, desc] = item.split(":")
                return {
                    key,
                    value,
                    type: parseInt(type),
                    desc
                }
            })
            if (this.dataType === 'data') {
                this.formData = data
            } else {
                this.paramsData = data
            }
        },
        handleBulkEdit() {
            this.showDialog = true
            const data = this.dataType === 'data' ? this.formData : this.paramsData
            this.textareaData = data.map(
                item => {
                    const flag = ':'
                    return `${item.key}${flag}${item.value}${flag}${item.type}${flag}${item.desc}`

                }
            ).join("\n")
        },
        uploadSuccess(response, file, fileList) {
            this.$notify({
                message: "上传成功",
                type: 'success',
                duration: 1000
            });
            
            // 删除旧文件（如果存在）
            const oldFileId = this.formData[this.currentIndex].file_id;
            if (oldFileId) {
                api.deleteFile(oldFileId).catch(() => {});
            }
            
            // 更新文件信息
            this.formData[this.currentIndex].value = file.name;
            this.formData[this.currentIndex].size = file.size;
            this.formData[this.currentIndex].file_id = response.id;
            
            // 强制更新组件以确保下次上传正常工作
            this.$forceUpdate();
        },
        
        uploadError(err, file, fileList) {
            console.error("上传错误:", err);
            this.$notify.error({
                message: "上传失败: " + (err.message || "请检查认证信息和网络连接"),
                duration: 3000
            });
        },

        uploadFile(row) {
            // 使用新的文件上传API，添加token参数
            return '/api/fastrunner/file/?token=' + this.authToken;
        },

        cellMouseEnter(row) {
            this.currentRow = row;
        },

        cellMouseLeave(row) {
            this.currentRow = '';
        },

        handleEdit(index, row) {
            const data = this.dataType === 'data' ? this.formData : this.paramsData;
            data.push({
                key: '',
                value: '',
                type: 1,
                desc: ''
            });
        },
        handleCopy(index, row) {
            const data = this.dataType === 'data' ? this.formData : this.paramsData;
            data.splice(index + 1, 0, {
                key: row.key,
                value: row.value,
                type: row.type,
                desc: row.desc
            });
        },
        handleDelete(index, row) {
            const data = this.dataType === 'data' ? this.formData : this.paramsData;
            data.splice(index, 1);
        },

        clearFile(index) {
            this.formData[index].value = '';
            this.formData[index].size = 0;
            this.formData[index].file_id = null;
        },

        // 文件格式化
        parseFile() {
            let files = {
                files: {},
                desc: {}
            };

            for (let content of this.formData) {
                // 是文件
                if (content['key'] !== '' && content['type'] === 5) {
                    files.files[content['key']] = content['value'];
                    files.desc[content['key']] = content['desc'];
                }
            }
            return files
        },

        // 表单格式化
        parseForm() {
            let form = {
                data: {},
                desc: {}
            };
            for (let content of this.formData) {
                // file 不处理
                if (content['key'] !== '' && content['type'] !== 5) {
                    const value = this.parseType(content['type'], content['value']);

                    if (value === 'exception') {
                        continue;
                    }

                    form.data[content['key']] = value;
                    form.desc[content['key']] = content['desc'];
                }
            }
            return form;
        },

        parseParams() {
            let params = {
                params: {},
                desc: {}
            };
            for (let content of this.paramsData) {
                if (content['key'] !== '') {
                    params.params[content['key']] = content['value'];
                    params.desc[content['key']] = content['desc'];
                }
            }
            return params;
        },

        parseJson() {
            // TODO 初始化json太绕了，需要重新整理
            let json = {};
            let jsonStr = this.request.json_data
            if (typeof (jsonStr) === "object") {
                return jsonStr
            }
            if (typeof (jsonStr) !== "undefined" && jsonStr !== '') {
                try {
                    json = JSON.parse(jsonStr);
                } catch (err) {
                    this.$notify.error({
                        title: 'json错误',
                        message: '不是标准的json数据格式',
                        duration: 2000
                    });
                }
            }
            return json;
        },

        // 类型转换
        parseType(type, value) {
            // 如果是File类型（type=5），直接返回原值，不进行任何处理
            if (type === 5) {
                return value;
            }
            
            let tempValue;
            const msg = value + ' => ' + this.dataTypeOptions[type - 1].label + ' 转换异常, 该数据自动剔除';
            switch (type) {
                case 1:
                    tempValue = value;
                    break;
                case 2:
                    tempValue = parseInt(value);
                    break;
                case 3:
                    tempValue = parseFloat(value);
                    break;
                case 4:
                    if (value === 'False' || value === 'True') {
                        let bool = {
                            'True': true,
                            'False': false
                        };
                        tempValue = bool[value];
                    } else {
                        this.$notify.error({
                            title: '类型转换错误',
                            message: msg,
                            duration: 2000
                        });
                        return 'exception'
                    }
                    break;
                case 6:
                    try {
                        tempValue = JSON.parse(value);
                    } catch (err) {
                        // 包含$是引用类型,可以任意类型
                        if (value.indexOf("$") != -1) {
                            tempValue = value
                        } else {
                            tempValue = false
                        }
                    }
                    break;
            }
            if (tempValue !== 0 && !tempValue && type !== 4 && type !== 1) {
                this.$notify.error({
                    title: '类型转换错误',
                    message: msg,
                    duration: 2000
                });
                return 'exception'
            }
            return tempValue;
        },

        notifyCopyRequest(jsonpath, title) {
            this.$notify.success({
                title: title,
                message: jsonpath,
                duration: 2000
            });
        }
    },

}
</script>

<style scoped>
/*.ace_editor {*/
/*    position: relative;*/
/*    overflow: hidden;*/
/*    font: 18px/normal 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace !important;*/
/*    direction: ltr;*/
/*    text-align: left;*/
/*    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);*/
/*}*/

.el-textarea__inner {
    border: none !important; /* 移除.el-textarea类的边框 */
    font-size: 18px; /* 设置字体大小 */
}
</style>
