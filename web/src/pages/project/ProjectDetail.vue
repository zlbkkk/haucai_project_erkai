<template>

    <div>
        <div style="padding: 10px 0; margin-bottom: 10px; display: flex; align-items: center;">
            <h2 style="margin: 10 10 10 10; font-size: 20px; color: #606266; font-weight: 500;">{{ projectInfo.name }}</h2>
            <p v-if="projectInfo.desc" style="margin: 0 0 0 15px; font-size: 14px; color: #909399;">项目描述：{{ projectInfo.desc }}</p>
        </div>

        <ul class="project_detail" style="display: none">
            <li class="pull-left">
                <p class="title-p"><i class="iconfont">&#xe74a;</i> &nbsp;{{ projectInfo.api_count }} 个接口</p>
                <p class="desc-p">接口总数</p>
            </li>
            <li class="pull-left">
                <p class="title-p"><i class="iconfont">&#xe61f;</i> &nbsp;{{ projectInfo.case_step_count }} 个监控接口</p>
                <p class="desc-p">监控接口个数</p>
            </li>
            <li class="pull-left">
                <p class="title-p"><i class="iconfont">&#xe61e;</i> &nbsp;{{ projectInfo.task_count }} 项任务</p>
                <p class="desc-p">定时任务个数</p>
            </li>

            <li class="pull-left">
                <p class="title-p"><i class="iconfont">&#xe6da;</i> &nbsp;{{ projectInfo.case_count }} 个用例</p>
                <p class="desc-p">用例集总数</p>
            </li>

        </ul>
        <ul class="project_detail" style="display: none">
            <!--            <li class="pull-left">-->
            <!--                <p class="title-p"><i class="iconfont">&#xe609;</i> &nbsp;{{ projectInfo.host_count }} 套环境</p>-->
            <!--                <p class="desc-p">环境总数</p>-->
            <!--            </li>            -->
            <li class="pull-left">
                <p class="title-p"><i class="iconfont">&#xe609;</i> &nbsp;{{ projectInfo.api_cover_rate }}% 接口覆盖率</p>
                <p class="desc-p">用例步骤和接口总数的比例</p>
            </li>
            <li class="pull-left">
                <p class="title-p"><i class="iconfont">&#xe66e;</i> 共 {{ projectInfo.report_count }} 个报告
                    {{ projectInfo.report_success }} 成功,{{ projectInfo.report_fail }} 失败 </p>
                <p class="desc-p">测试报告总数</p>
            </li>
            <li class="pull-left">
                <p class="title-p"><i class="iconfont">&#xee32;</i> &nbsp;{{ projectInfo.config_count }} 套配置</p>
                <p class="desc-p">配置总数</p>
            </li>
            <li class="pull-left">
                <p class="title-p"><i class="iconfont">&#xe692;</i> &nbsp;{{ projectInfo.variables_count }} 对变量</p>
                <p class="desc-p">全局变量对数</p>
            </li>
        </ul>

        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <el-card style="width: 30%; max-height: 300px;">
                <div slot="header">
                    <span>API</span>
                    <i class="iconfont">&#xe74a;</i>
                </div>
                <el-row type="flex">
                    <el-col :span="24">
                        <ApexCharts height="130" :options="apiPieOptions" :series="apiPieSeries"></ApexCharts>
                    </el-col>
                </el-row>
                <el-row type="flex" justify="center">
                    <el-col :span="16">
                        <ApexCharts height="100" :options="apiCoverRateOptions" :series="apiCoverRateSeries"></ApexCharts>
                    </el-col>
                </el-row>
            </el-card>

            <el-card style="width: 30%; max-height: 300px;">
                <div slot="header">
                    <span>Case</span>
                    <i class="iconfont">&#xe6da;</i>
                </div>
                <el-row type="flex">
                    <el-col :span="24">
                        <ApexCharts height="130" :options="casePieOptions" :series="casePieSeries"></ApexCharts>
                    </el-col>
                </el-row>

                <el-row type="flex" justify="center">
                    <el-col :span="16">
                        <ApexCharts height="100" :options="coreCaseCoverRateOptions" :series="coreCaseCoverRateSeries"></ApexCharts>
                    </el-col>
                </el-row>
            </el-card>
            <el-card style="width: 30%; max-height: 300px;">
                <div slot="header">
                    <span>Report</span>
                    <i class="iconfont">&#xe66e;</i>
                </div>
                <ApexCharts height="230" :options="reportPieOptions" :series="reportPieSeries"></ApexCharts>
            </el-card>

        </div>

        <div style="display: flex; justify-content: space-around; margin-top: 10px;">
            <el-card style="width: 30%;">
                <div slot="header">
                    <span>API每日创建</span>
                    <i class="iconfont">&#xe74a;</i>
                </div>

                <ApexCharts height="200" type="area" :options="apiAreaOptions" :series="apiAreaSeries"></ApexCharts>
            </el-card>
            <el-card style="width: 30%">
                <div slot="header">
                    <span>Case每日创建</span>
                    <i class="iconfont">&#xe6da;</i>
                </div>
                <ApexCharts height="200" type="area" :options="caseAreaOptions" :series="caseAreaSeries"></ApexCharts>
            </el-card>
            <el-card style="width: 30%">
                <div slot="header">
                    <span>Report每日创建</span>
                    <i class="iconfont">&#xe66e;</i>
                </div>
                <ApexCharts height="200" type="area" :options="reportAreaOptions" :series="reportAreaSeries"></ApexCharts>
            </el-card>

        </div>
    </div>
</template>

<script>

export default {
    name: "ProjectDetail",
    data() {
        return {

            visitInfo: {},
            projectInfo: {},
            apiPieOptions: {
                plotOptions: {
                    pie: {
                        donut: {
                            size: '50%',
                            labels: {
                                show: true,
                                total: {
                                    show: true,
                                    showAlways: true,
                                    label: 'Total',
                                }
                            },
                        }
                    }
                },
                show: true,
                chart: {
                    id: "apiPie",
                    type: "donut",
                },
                legend: {
                    show: true,
                    position: 'right',
                    offsetY: 0,
                    fontSize: '12px',
                    formatter: function(val, opts) {
                        return val;
                    }
                },
                // 饼图右上角的分类，会被接口返回值的覆盖
                labels: ['手动创建的API', '从YAPI导入API',]
            },
            apiCoverRateSeries: [],
            coreCaseCoverRateSeries: [],
            apiCoverRateOptions: {
                chart: {
                    height: 150,
                    type: "radialBar"
                },
                colors: ["#2196F3"],
                plotOptions: {
                    radialBar: {
                        hollow: {
                            margin: 0,
                            size: "60%"
                        },
                        track: {
                            background: "#f2f2f2",
                            strokeWidth: '100%'
                        },
                        dataLabels: {
                            showOn: "always",
                            name: {
                                show: true,
                                color: "#888",
                                fontSize: "14px",
                                offsetY: 30
                            },
                            value: {
                                color: "#111",
                                fontSize: "18px",
                                show: true,
                                offsetY: -10,
                                formatter: function(val) {
                                    return val + "%";
                                }
                            },
                            position: "outside"
                        }
                    }
                },
                stroke: {
                    lineCap: "round",
                },
                labels: ["接口覆盖"]
            },
            coreCaseCoverRateOptions: {
                chart: {
                    height: 150,
                    type: "radialBar"
                },
                colors: ["#4CAF50"],
                plotOptions: {
                    radialBar: {
                        hollow: {
                            margin: 0,
                            size: "60%"
                        },
                        track: {
                            background: "#f2f2f2",
                            strokeWidth: '100%'
                        },
                        dataLabels: {
                            showOn: "always",
                            name: {
                                show: true,
                                color: "#888",
                                fontSize: "14px",
                                offsetY: 30
                            },
                            value: {
                                color: "#111",
                                fontSize: "18px",
                                show: true,
                                offsetY: -10,
                                formatter: function(val) {
                                    return val + "%";
                                }
                            },
                            position: "outside"
                        }
                    }
                },
                stroke: {
                    lineCap: "round",
                },
                labels: ["核心覆盖"]
            },
            casePieOptions: {
                plotOptions: {
                    pie: {
                        donut: {
                            size: '50%',
                            labels: {
                                show: true,
                                total: {
                                    show: true,
                                    showAlways: true,
                                    label: 'Total',
                                }
                            },
                        }
                    }
                },
                show: true,
                chart: {
                    id: "casePie",
                    type: "donut",
                },
                legend: {
                    show: true,
                    position: 'right',
                    offsetY: 0,
                    fontSize: '12px',
                    formatter: function(val, opts) {
                        return val;
                    }
                },
                // 饼图右上角的分类，会被接口返回值的覆盖
                labels: ['冒烟用例', '集成用例', '监控脚本', '核心用例']
            },
            reportPieOptions: {
                plotOptions: {
                    pie: {
                        donut: {
                            size: '50%',
                            labels: {
                                show: true,
                                total: {
                                    show: true,
                                    showAlways: true,
                                    label: 'Total',
                                }
                            },
                        }
                    }
                },
                show: true,
                chart: {
                    type: "donut",
                },
                legend: {
                    show: true,
                    position: 'right',
                    offsetY: 0,
                    fontSize: '12px',
                    formatter: function(val, opts) {
                        return val;
                    }
                },
                // 饼图右上角的分类，会被接口返回值的覆盖
                labels: ['调试', '异步', '定时', '部署',]
            },
            apiPieSeries: [],
            casePieSeries: [],
            reportPieSeries: [],
            visitChartOptions: {
                chart: {
                    id: 'vuechart-example',
                },
                xaxis: {
                    categories: []
                }
            },
            apiAreaOptions: {
                chart: {
                    foreColor: "#aaa",
                    id: 'apiArea',
                },
                xaxis: {
                    categories: []
                }
            },
            caseAreaOptions: {
                chart: {
                    id: 'caseArea',
                },
                xaxis: {
                    categories: []
                }
            },
            reportAreaOptions: {
                chart: {
                    id: 'reportArea',
                },
                xaxis: {
                    categories: []
                }
            },
            visitSeries: [{
                name: '访问量',
                data: []
            }],
            apiAreaSeries: [{
                name: 'API创建数量',
                data: []
            }],
            caseAreaSeries: [{
                name: 'Case创建数量',
                data: []
            }],
            reportAreaSeries: [{
                name: 'Report创建数量',
                data: []
            }],
        }
    },
    methods: {
        getVisitData() {
            const project = this.$route.params.id;
            this.$api.getVisit({
                params: {
                    project: project
                }
            }).then(res => {
                this.visitChartOptions = {...this.visitChartOptions, ...{xaxis: {categories: res.recent7days}}}
            })
        },
        success(resp) {
            this.$notify({
                message: resp["msg"],
                type: 'success',
                duration: this.$store.state.duration
            });
        },
        failure(resp) {
            this.$notify.error({
                message: resp.msg,
                duration: this.$store.state.duration
            });
        },

        handleArea() {
            const res = this.projectInfo.daily_create_count
            const apiDays = res.api.days
            const caseDays = res.case.days
            const reportDays = res.report.days
            const apiCount = res.api.count
            const caseCount = res.case.count
            const reportCount = res.report.count
            this.apiAreaOptions = {...this.apiAreaOptions, ...{xaxis: {categories: apiDays}}}
            this.caseAreaOptions = {...this.caseAreaOptions, ...{xaxis: {categories: caseDays}}}
            this.reportAreaOptions = {...this.reportAreaOptions, ...{xaxis: {categories: reportDays}}}
            this.apiAreaSeries[0].data = apiCount
            this.caseAreaSeries[0].data = caseCount
            this.reportAreaSeries[0].data = reportCount

            this.apiCoverRateSeries.push(this.projectInfo.api_cover_rate)
            this.coreCaseCoverRateSeries.push(this.projectInfo.core_case_cover_rate)
        },
        handlePie() {
            const pi = this.projectInfo
            this.apiPieSeries = pi.api_count_by_create_type.count
            this.apiPieOptions = {...this.apiPieOptions, ...{labels: pi.api_count_by_create_type.type}}

            this.casePieSeries = pi.case_count_by_tag.count
            this.casePieOptions = {...this.casePieOptions, ...{labels: pi.case_count_by_tag.tag}}

            this.reportPieSeries = pi.report_count_by_type.count
            this.reportPieOptions = {...this.reportPieOptions, ...{labels: pi.report_count_by_type.type}}
        },
        getProjectDetail() {
            const pk = this.$route.params.id;
            this.$api.getProjectDetail(pk).then(res => {
                this.projectInfo = res
                this.handleArea()
                this.handlePie()
            })
        }
    },
    mounted() {
        this.getVisitData()
        this.getProjectDetail();
    },

    beforeMount() {
    }

}
</script>

<style scoped>


.desc-p {
    padding-top: 10px;
    font-size: 12px;
    color: #b6b6b6;
}

.title-p {
    font-size: 18px;
    margin-top: 10px;
}

.title-project li a {
    font-size: 12px;
    text-decoration: none;
    color: #a3a3a3;
    margin-left: 20px;

}

.pull-left {
    float: left;
    margin-left: 10px;
}

.project_detail li {
    margin-top: 10px;
    text-indent: 20px;
    display: inline-block;
    height: 90px;
    width: calc(20% - 1.5px);
    border: 1px solid #ddd;
}

.project_detail {
    height: 100px;
    margin-top: 20px;
}

.title-project {
    margin-top: 40px;
    margin-left: 10px;
}

ul li {
    list-style: none;
}

.title-li {
    font-size: 24px;
    color: #607d8b;
}

.desc-li {
    margin-top: 10px;
    color: #b6b6b6;
    font-size: 14px;
}
</style>
