{{/*
Expand the name of the chart.
*/}}
{{- define "fme-mcp-ultra.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "fme-mcp-ultra.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "fme-mcp-ultra.labels" -}}
helm.sh/chart: {{ include "fme-mcp-ultra.name" . }}-{{ .Chart.Version | replace "+" "_" }}
{{ include "fme-mcp-ultra.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "fme-mcp-ultra.selectorLabels" -}}
app.kubernetes.io/name: {{ include "fme-mcp-ultra.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

