<template>
    <el-container>
        <el-header style="background: #F7F7F7; padding: 0; height: 50px">
            <div>
                <div style="padding-top: 10px; margin-left: 10px;">
                    <el-button
                        type="primary"
                        size="small"
                        icon="el-icon-circle-plus"
                        :title="isSuperuser ? '添加项目' : '权限不足，请联系管理员'"
                        :disabled="!isSuperuser"
                        @click="dialogVisible = true"
                    >
                        添加项目
                    </el-button>
                    <el-button type="success" size="small" icon="el-icon-data-line" @click="dashBoardVisible = true">
                        项目看板
                    </el-button>

                    <el-button
                        style="margin-left: 50px"
                        type="info"
                        round
                        size="small"
                        icon="el-icon-d-arrow-left"
                        :disabled="projectData.previous === null"
                        @click="getPagination(projectData.previous)"
                    >
                        上一页
                    </el-button>

                    <el-button
                        type="info"
                        round
                        size="small"
                        :disabled="projectData.next === null"
                        @click="getPagination(projectData.next)"
                    >
                        下一页
                        <i class="el-icon-d-arrow-right"></i>
                    </el-button>

                    <el-dialog title="添加项目" :visible.sync="dialogVisible" width="30%" align="center">
                        <el-form
                            :model="projectForm"
                            :rules="rules"
                            ref="projectForm"
                            label-width="150px"
                            class="project"
                        >
                            <el-form-item label="项目名称" prop="name">
                                <el-input v-model="projectForm.name" clearable></el-input>
                            </el-form-item>

                            <el-form-item label="项目描述" prop="desc">
                                <el-input v-model="projectForm.desc" clearable></el-input>
                            </el-form-item>

                            <el-form-item label="负责人" prop="responsible">
                                <el-select
                                    v-model="projectForm.responsible"
                                    placeholder="请选择项目负责人"
                                    filterable
                                    clearable
                                    :style="{ width: '100%' }"
                                >
                                    <el-option
                                        v-for="(item, index) in responsibleOptions"
                                        :key="index"
                                        :label="item.label"
                                        :value="item.value"
                                        :disabled="item.disabled"
                                    ></el-option>
                                </el-select>
                            </el-form-item>

                            <el-form-item label="YAPI地址" prop="yapi_base_url">
                                <el-input v-model="projectForm.yapi_base_url" clearable></el-input>
                            </el-form-item>

                            <el-form-item label="YAPI token" prop="yapi_openapi_token">
                                <el-input v-model="projectForm.yapi_openapi_token" clearable></el-input>
                            </el-form-item>

                            <el-form-item label="JIRA bearer token" prop="jira_bearer_token">
                                <el-input v-model="projectForm.jira_bearer_token" clearable></el-input>
                            </el-form-item>

                            <el-form-item label="JIRA project_key" prop="jira_project_key">
                                <el-input v-model="projectForm.jira_project_key" clearable></el-input>
                            </el-form-item>
                        </el-form>
                        <span slot="footer" class="dialog-footer">
                            <el-button @click="closeAddDialog">取 消</el-button>
                            <el-button type="primary" @click="handleConfirm('projectForm')">确 定</el-button>
                        </span>
                    </el-dialog>
                </div>
            </div>
        </el-header>

        <el-drawer
            style="margin-top: 10px"
            :destroy-on-close="true"
            :with-header="false"
            :modal="false"
            size="89%"
            :visible.sync="dashBoardVisible"
        >
            <ProjectDashBoard></ProjectDashBoard>
        </el-drawer>

        <el-container>
            <el-main style="padding: 0; margin-left: 10px">
                <el-table
                    :data="projectData.results"
                    border
                    stripe
                    :show-header="projectData.results.length > 0"
                    highlight-current-row
                    style="width: 100%;"
                >
                    <el-table-column label="操作" align="center" width="180">
                        <template slot-scope="scope">
                            <div style="white-space: nowrap;">
                                <el-button
                                    size="mini"
                                    type="primary"
                                    @click="handleCellClick(scope.row)"
                                    style="margin-right: 3px; padding: 5px 8px;"
                                    >进入
                                </el-button>

                                <el-button
                                    size="mini"
                                    type="warning"
                                    title="编辑"
                                    @click="handleEdit(scope.row)"
                                    style="margin-right: 3px; padding: 5px 8px;"
                                    >编辑
                                </el-button>

                                <el-button
                                    size="mini"
                                    type="danger"
                                    :title="isSuperuser ? '删除项目' : '权限不足，请联系管理员'"
                                    :disabled="!isSuperuser"
                                    @click="handleDelete(scope.row)"
                                    style="padding: 5px 8px;"
                                    >删除
                                </el-button>
                            </div>
                        </template>
                    </el-table-column>

                    <el-table-column label="项目名称" width="250" align="center">
                        <template slot-scope="scope">
                            <span
                                style="font-size: 18px; font-weight: bold; cursor: pointer;"
                                @click="handleCellClick(scope.row)"
                                >{{ scope.row.name }}</span
                            >
                        </template>
                    </el-table-column>

                    <el-table-column label="负责人" width="200" align="center">
                        <template slot-scope="scope">
                            <span>{{ scope.row.responsible }}</span>
                        </template>
                    </el-table-column>

                    <el-table-column label="项目描述" width="300" align="center">
                        <template slot-scope="scope">
                            <span>{{ scope.row.desc }}</span>
                        </template>
                    </el-table-column>

                    <el-table-column label="更新时间" width="260" align="center">
                        <template slot-scope="scope">
                            <span>{{ scope.row.update_time | datetimeFormat }}</span>
                        </template>
                    </el-table-column>
                </el-table>
            </el-main>
        </el-container>

        <!-- 编辑项目对话框 -->
        <el-dialog title="编辑项目" :visible.sync="editVisible" width="30%">
            <el-form :model="projectForm" :rules="rules" ref="projectForm" label-width="150px">
                <el-form-item label="项目名称" prop="name">
                    <el-input v-model="projectForm.name" clearable></el-input>
                </el-form-item>
                <el-form-item label="项目描述" prop="desc">
                    <el-input v-model="projectForm.desc" clearable></el-input>
                </el-form-item>
                <el-form-item label="负责人" prop="responsible">
                    <el-select
                        v-model="projectForm.responsible"
                        placeholder="请选择项目负责人"
                        filterable
                        clearable
                        :style="{ width: '100%' }"
                    >
                        <el-option
                            v-for="(item, index) in responsibleOptions"
                            :key="index"
                            :label="item.label"
                            :value="item.value"
                            :disabled="item.disabled"
                        ></el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="YAPI地址" prop="yapi_base_url">
                    <el-input v-model="projectForm.yapi_base_url" clearable></el-input>
                </el-form-item>

                <el-form-item label="YAPI token" prop="yapi_openapi_token">
                    <el-input v-model="projectForm.yapi_openapi_token" clearable></el-input>
                </el-form-item>
                <el-form-item label="JIRA bearer token" prop="jira_bearer_token">
                    <el-input v-model="projectForm.jira_bearer_token" clearable></el-input>
                </el-form-item>
                <el-form-item label="JIRA project_key" prop="jira_project_key">
                    <el-input v-model="projectForm.jira_project_key" clearable></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <el-button @click="closeEditDialog">取 消</el-button>
                <el-button type="primary" @click="handleConfirm('projectForm')">确 定</el-button>
            </span>
        </el-dialog>
    </el-container>
</template>

<script>
import ProjectDashBoard from './ProjectDashBoard'

export default {
    components: {
        ProjectDashBoard
    },
    data() {
        return {
            isSuperuser: this.$store.state.is_superuser,
            userName: this.$store.state.user,
            dialogVisible: false,
            dashBoardVisible: false,
            editVisible: false,
            projectData: {
                results: []
            },
            projectForm: {
                name: '',
                desc: '',
                responsible: this.$store.state.user,
                id: '',
                yapi_base_url: '',
                yapi_openapi_token: '',
                jira_bearer_token: '',
                jira_project_key: ''
            },
            responsibleOptions: [],
            rules: {
                name: [
                    { required: true, message: '请输入项目名称', trigger: 'blur' },
                    { min: 1, max: 50, message: '最多不超过50个字符', trigger: 'blur' }
                ],
                desc: [
                    { required: true, message: '简要描述下该项目', trigger: 'blur' },
                    { min: 1, max: 100, message: '最多不超过100个字符', trigger: 'blur' }
                ],
                responsible: [
                    {
                        required: true,
                        message: '请选择项目负责人',
                        trigger: 'change'
                    }
                ],
                yapi_base_url: [{ required: false, message: 'YAPI openapi的url', trigger: 'blur' }],
                yapi_openapi_token: [{ required: false, message: 'YAPI openapi的token', trigger: 'blur' }],
                jira_bearer_token: [{ required: false, message: 'JIRA bearer_token', trigger: 'blur' }],
                jira_project_key: [{ required: false, message: 'jira_project_key', trigger: 'blur' }]
            }
        }
    },
    methods: {
        handleCellClick(row) {
            this.$store.commit('setRouterName', 'ProjectDetail')
            this.$store.commit('setProjectName', row.name)
            this.setLocalValue('routerName', 'ProjectDetail')
            // 在vuex严格模式下, commit会经过mutation函数不会报错, set直接修改会报错
            this.setLocalValue('projectName', row.name)
            this.$router.push({ name: 'ProjectDetail', params: { id: row['id'] } })
        },
        handleEdit(row) {
            if (!(this.isSuperuser || this.userName === row.responsible)) {
                this.$message.error({
                    message: '权限不足，请联系管理员',
                    duration: this.$store.state.duration
                })
                return
            }

            this.editVisible = true
            this.projectForm.name = row['name']
            this.projectForm.desc = row['desc']
            this.projectForm.responsible = row['responsible']
            this.projectForm.id = row['id']
            this.projectForm.yapi_base_url = row['yapi_base_url']
            this.projectForm.yapi_openapi_token = row['yapi_openapi_token']
            this.projectForm.jira_project_key = row['jira_project_key']
            this.projectForm.jira_bearer_token = row['jira_bearer_token']
        },
        handleDelete(row) {
            this.$confirm('此操作将永久删除该项目, 是否继续?', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                this.$api.deleteProject({ data: { id: row['id'] } }).then(resp => {
                    if (resp['success']) {
                        this.success(resp)
                        this.getProjectList()
                    } else {
                        this.failure(resp)
                    }
                })
            })
        },
        handleConfirm(formName) {
            this.$refs[formName].validate(valid => {
                if (valid) {
                    this.dialogVisible = false
                    this.editVisible = false
                    let obj

                    if (this.projectForm.id === '') {
                        obj = this.$api.addProject(this.projectForm)
                    } else {
                        obj = this.$api.updateProject(this.projectForm)
                    }

                    obj.then(resp => {
                        if (resp.success) {
                            this.success(resp)
                            this.getProjectList()
                        } else {
                            this.failure(resp)
                        }
                        this.resetProjectForm()
                    })
                } else {
                    if (this.projectForm.id !== '') {
                        this.editVisible = true
                    } else {
                        this.dialogVisible = true
                    }
                    return false
                }
            })
        },
        success(resp) {
            this.$notify({
                message: resp['msg'],
                type: 'success',
                duration: this.$store.state.duration
            })
        },
        failure(resp) {
            this.$notify.error({
                message: resp['msg'],
                duration: this.$store.state.duration
            })
        },
        getProjectList() {
            this.$api.getProjectList().then(resp => {
                this.projectData = resp
            })
        },
        getPagination(url) {
            this.$api.getPagination(url).then(resp => {
                this.projectData = resp
            })
        },
        closeEditDialog() {
            this.editVisible = false
            this.resetProjectForm()
        },
        closeAddDialog() {
            this.dialogVisible = false
            this.resetProjectForm()
        },
        resetProjectForm() {
            this.projectForm.name = ''
            this.projectForm.desc = ''
            this.projectForm.responsible = ''
            this.projectForm.id = ''
            this.projectForm.yapi_openapi_token = ''
            this.projectForm.yapi_base_url = ''
            this.projectForm.jira_bearer_token = ''
            this.projectForm.jira_project_key = ''
        },
        getUserList() {
            this.$api.getUserList().then(resp => {
                for (let i = 0; i < resp.length; i++) {
                    this.responsibleOptions.push({ label: resp[i].username, value: resp[i].username })
                }
            })
        }
    },
    created() {
        this.getProjectList()
        this.getUserList()
    },
    name: 'ProjectList'
}
</script>

<style scoped></style>
