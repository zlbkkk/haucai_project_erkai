import datetime
import os
import uuid

import coreapi
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError
from django.db.models import Q
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.viewsets import GenericViewSet

from fastrunner import models, serializers
from fastrunner.utils import response
from fastrunner.utils.decorator import request_log
from fastrunner.utils.prepare import get_project_filter_condition
from fastrunner.utils.parser import Format, Parse


class APITemplateViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ("get",):
            extra_fields = [
                coreapi.Field("node"),
                coreapi.Field("project"),
                coreapi.Field("search"),
                coreapi.Field("tag"),
                coreapi.Field("rigEnv"),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class APITemplateView(GenericViewSet):
    """
    API操作视图
    """

    serializer_class = serializers.APISerializer
    queryset = models.API.objects.filter(~Q(tag=4))
    schema = APITemplateViewSchema()

    @swagger_auto_schema(query_serializer=serializers.AssertSerializer)
    @method_decorator(request_log(level="DEBUG"))
    def list(self, request):
        """
        api-获取api列表

        支持多种条件搜索
        """
        ser = serializers.AssertSerializer(data=request.query_params)
        if ser.is_valid():
            node = ser.validated_data.get("node")
            project = ser.validated_data.get("project")
            search: str = ser.validated_data.get("search")
            tag = ser.validated_data.get("tag")
            rig_env = ser.validated_data.get("rigEnv")
            delete = ser.validated_data.get("delete")
            only_me = ser.validated_data.get("onlyMe")
            showYAPI = ser.validated_data.get("showYAPI")
            creator = ser.validated_data.get("creator")

            # 使用新的过滤条件，包含当前项目和公共项目的数据
            project_filter = get_project_filter_condition(project)
            queryset = self.get_queryset().filter(project_filter).filter(delete=delete).order_by("-update_time")

            if only_me is True:
                queryset = queryset.filter(creator=request.user)

            if creator:
                queryset = queryset.filter(creator=creator)

            if showYAPI is False:
                queryset = queryset.filter(~Q(creator="yapi"))

            if search != "":
                search: list = search.split()
                for key in search:
                    queryset = queryset.filter(Q(name__contains=key) | Q(url__contains=key))

            if node != "":
                queryset = queryset.filter(relation=node)

            if tag != "":
                # 支持多个状态筛选，以逗号分隔
                if ',' in tag:
                    tag_list = tag.split(',')
                    tag_filter = Q()
                    for t in tag_list:
                        # 确保每个标签值是有效的
                        try:
                            t = int(t.strip())
                            if t in dict(models.API.TAG).keys():
                                tag_filter |= Q(tag=t)
                        except (ValueError, TypeError):
                            continue
                    queryset = queryset.filter(tag_filter)
                else:
                    # 单个标签值的处理
                    try:
                        tag_value = int(tag)
                        if tag_value in dict(models.API.TAG).keys():
                            queryset = queryset.filter(tag=tag_value)
                    except (ValueError, TypeError):
                        pass

            if rig_env != "":
                queryset = queryset.filter(rig_env=rig_env)

            pagination_queryset = self.paginate_queryset(queryset)
            serializer = self.get_serializer(pagination_queryset, many=True)

            return self.get_paginated_response(serializer.data)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(request_log(level="INFO"))
    def add(self, request):
        """
        api-新增一个api

        前端按照格式组装好，注意body
        """

        api = Format(request.data)
        api.parse()

        api_body = {
            "name": api.name,
            "body": api.testcase,
            "url": api.url,
            "method": api.method,
            "project": models.Project.objects.get(id=api.project),
            "relation": api.relation,
            "creator": request.user.username,
        }

        try:
            models.API.objects.create(**api_body)
        except DataError:
            return Response(response.DATA_TO_LONG)

        return Response(response.API_ADD_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def update(self, request, **kwargs):
        """
        api-更新单个api

        更新单个api的内容
        """
        pk = kwargs["pk"]
        
        # 添加调试信息
        print(f"DEBUG: Received request.data keys: {list(request.data.keys()) if hasattr(request.data, 'keys') else 'not dict'}")
        if hasattr(request.data, 'get') and request.data.get('request'):
            print(f"DEBUG: request.request keys: {list(request.data.get('request', {}).keys())}")
            if request.data.get('request', {}).get('form'):
                print(f"DEBUG: request.request.form: {request.data['request']['form']}")
            if request.data.get('request', {}).get('files'):
                print(f"DEBUG: request.request.files: {request.data['request']['files']}")
        
        api = Format(request.data)
        api.parse()

        api_body = {
            "name": api.name,
            "body": api.testcase,
            "url": api.url,
            "method": api.method,
            "updater": request.user.username,
        }

        try:
            models.API.objects.filter(id=pk).update(**api_body)
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def move(self, request):
        """
        api-批量更新api的目录

        移动api到指定目录
        """
        project: int = request.data.get("project")
        relation: int = request.data.get("relation")
        apis: list = request.data.get("api")
        ids = [api["id"] for api in apis]

        try:
            models.API.objects.filter(project=project, id__in=ids).update(relation=relation)
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def copy(self, request, **kwargs):
        """
        api-复制api

        复制一个api
        """
        pk = kwargs["pk"]
        name = request.data["name"]
        api = models.API.objects.get(id=pk)
        body = eval(api.body)
        body["name"] = name
        api.body = body
        api.id = None
        api.name = name
        api.creator = request.user.username
        api.updater = request.user.username
        api.save()
        return Response(response.API_ADD_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def delete(self, request, **kwargs):
        """
        api-删除一个api

        软删除一个api
        """

        try:
            if kwargs.get("pk"):  # 单个删除
                # models.API.objects.get(id=kwargs['pk']).delete()
                models.API.objects.filter(id=kwargs["pk"]).update(delete=1, update_time=datetime.datetime.now())
            else:
                for content in request.data:
                    # models.API.objects.get(id=content['id']).delete()
                    models.API.objects.filter(id=content["id"]).update(delete=1)

        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_DEL_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def add_tag(self, request, **kwargs):
        """
        api-更新api的tag,暂时默认为调试成功

        更新api的tag类型
        """
        api_ids: list = request.data.get("api_ids", [])
        try:
            if api_ids:
                models.API.objects.filter(pk__in=api_ids).update(
                    tag=request.data["tag"], update_time=datetime.datetime.now(), updater=request.user.username
                )
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        return Response(response.API_UPDATE_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def sync_case(self, request, **kwargs):
        """
        api-同步api的到case_step

        1.根据api_id查出("name", "body", "url", "method")
        2.根据api_id更新case_step中的("name", "body", "url", "method", "updater")
        3.更新case的update_time, updater
        """
        pk = kwargs["pk"]
        source_api = models.API.objects.filter(pk=pk).values("name", "body", "url", "method", "project").first()
        # 根据api反向查出project
        project = source_api.pop("project")

        project_case_ids = models.Case.objects.filter(project=project).values_list("id", flat=True)
        # 限制case_step只在当前项目
        case_steps = models.CaseStep.objects.filter(source_api_id=pk, case_id__in=project_case_ids)

        case_steps.update(**source_api, updater=request.user.username, update_time=datetime.datetime.now())
        case_ids = case_steps.values_list("case", flat=True)
        # 限制case只在当前项目
        models.Case.objects.filter(pk__in=list(case_ids), project=project).update(
            update_time=datetime.datetime.now(), updater=request.user.username
        )
        return Response(response.CASE_STEP_SYNC_SUCCESS)

    @method_decorator(request_log(level="INFO"))
    def single(self, request, **kwargs):
        """
        api-获取单个api详情，返回body信息

        获取单个api的详细情况
        """
        try:
            api = models.API.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return Response(response.API_NOT_FOUND)

        try:
            # 安全地解析 body 数据
            body_data = eval(api.body) if api.body else {}
            if not isinstance(body_data, dict):
                body_data = {}
        except (SyntaxError, ValueError, TypeError):
            body_data = {}

        parse = Parse(body_data)
        parse.parse_http()

        resp = {
            "id": api.id,
            "body": parse.testcase,
            "success": True,
            "creator": api.creator,
            "relation": api.relation,
            "project": api.project.id,
        }

        return Response(resp)


class APIFileView(GenericViewSet):
    """
    API文件上传视图
    """
    serializer_class = serializers.APIFileSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    @method_decorator(request_log(level="INFO"))
    def upload(self, request):
        """
        上传API文件
        """
        try:
            # 获取上传的文件
            file_obj = request.FILES.get('file')
            if not file_obj:
                return Response({"message": "未找到上传的文件"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 记录文件信息
            print(f"DEBUG: 上传文件名: {file_obj.name}")
            print(f"DEBUG: 文件大小: {file_obj.size} bytes")
            print(f"DEBUG: 文件类型: {file_obj.content_type}")
            
            # 检查文件大小限制 (50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            if file_obj.size > max_size:
                return Response({"message": f"文件大小超过限制，最大支持50MB，当前文件大小: {file_obj.size/1024/1024:.2f}MB"}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # 获取项目ID和API ID
            project_id = request.data.get('project')
            api_id = request.data.get('api')
            
            print(f"DEBUG: 项目ID: {project_id}, API ID: {api_id}")
            
            if not project_id:
                return Response({"message": "缺少项目ID"}, status=status.HTTP_400_BAD_REQUEST)
                
            # 获取项目信息
            try:
                project = models.Project.objects.get(id=project_id)
                print(f"DEBUG: 找到项目: {project.name}")
            except ObjectDoesNotExist:
                return Response({"message": "项目不存在"}, status=status.HTTP_404_NOT_FOUND)
                
            # 获取API信息（如果有）
            api = None
            if api_id:
                try:
                    api = models.API.objects.get(id=api_id)
                    print(f"DEBUG: 找到API: {api.name}")
                except ObjectDoesNotExist:
                    return Response({"message": "API不存在"}, status=status.HTTP_404_NOT_FOUND)
            
            # 创建文件存储目录
            file_dir = os.path.join(settings.BASE_DIR, 'file', project.name)
            print(f"DEBUG: 文件存储目录: {file_dir}")
            
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)
                print(f"DEBUG: 创建了目录: {file_dir}")
                
            # 生成唯一文件名
            file_name = file_obj.name
            file_ext = os.path.splitext(file_name)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(file_dir, unique_filename)
            
            print(f"DEBUG: 原文件名: {file_name}")
            print(f"DEBUG: 文件扩展名: {file_ext}")
            print(f"DEBUG: 唯一文件名: {unique_filename}")
            print(f"DEBUG: 完整文件路径: {file_path}")
            
            # 保存文件
            try:
                with open(file_path, 'wb+') as destination:
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
                print(f"DEBUG: 文件保存成功: {file_path}")
            except Exception as file_save_error:
                print(f"ERROR: 文件保存失败: {str(file_save_error)}")
                return Response({"message": f"文件保存失败: {str(file_save_error)}"}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            # 保存文件信息到数据库
            file_data = {
                'name': file_name,
                'file_path': os.path.join('file', project.name, unique_filename),
                'file_size': file_obj.size,
                'file_type': file_ext.lstrip('.') if file_ext else 'unknown',
                'project': project.id,
                'description': request.data.get('description', ''),
                'creator': request.user.username if hasattr(request.user, 'username') else 'anonymous'
            }
            
            if api:
                file_data['api'] = api.id
                
            print(f"DEBUG: 准备保存的文件数据: {file_data}")
            
            serializer = self.get_serializer(data=file_data)
            if serializer.is_valid():
                saved_file = serializer.save()
                print(f"DEBUG: 数据库保存成功, ID: {saved_file.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(f"ERROR: 序列化器验证失败: {serializer.errors}")
                # 如果保存失败，删除已上传的文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"DEBUG: 已删除失败的文件: {file_path}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"ERROR: 文件上传异常:")
            print(error_detail)
            return Response({"message": f"文件上传失败: {str(e)}", "detail": error_detail}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(request_log(level="INFO"))
    def list(self, request):
        """
        获取API文件列表
        """
        project_id = request.query_params.get('project')
        api_id = request.query_params.get('api')

        if not project_id:
            return Response({"message": "缺少项目ID"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = models.APIFile.objects.filter(project_id=project_id)

        if api_id:
            queryset = queryset.filter(api_id=api_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @method_decorator(request_log(level="INFO"))
    def delete(self, request, **kwargs):
        """
        删除API文件
        """
        try:
            pk = kwargs.get('pk')
            file_obj = models.APIFile.objects.get(id=pk)

            # 删除物理文件
            file_path = os.path.join(settings.BASE_DIR, file_obj.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)

            # 删除数据库记录
            file_obj.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"message": "文件不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"删除文件失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
