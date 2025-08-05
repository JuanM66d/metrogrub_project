import json as json_lib

from IPython.display import HTML, display
import altair as alt
from google.protobuf import field_mask_pb2
from google.protobuf.json_format import MessageToDict
import pandas as pd
import proto

def handle_text_response(resp):
    parts = getattr(resp, "parts")
    print("".join(parts))


def display_schema(data):
    fields = getattr(data, "fields")
    df = pd.DataFrame(
        {
            "Column": map(lambda field: getattr(field, "name"), fields),
            "Type": map(lambda field: getattr(field, "type"), fields),
            "Description": map(
                lambda field: getattr(field, "description", "-"), fields
            ),
            "Mode": map(lambda field: getattr(field, "mode"), fields),
        }
    )
    display(df)


def display_section_title(text):
    display(HTML(f"<h2>{text}</h2>"))


def format_looker_table_ref(table_ref):
    return f"lookmlModel: {table_ref.lookml_model}, explore: {table_ref.explore}, lookerInstanceUri: {table_ref.looker_instance_uri}"


def format_bq_table_ref(table_ref):
    return f"{table_ref.project_id}.{table_ref.dataset_id}.{table_ref.table_id}"


def display_datasource(datasource):
    source_name = ""
    if "studio_datasource_id" in datasource:
        source_name = getattr(datasource, "studio_datasource_id")
    elif "looker_explore_reference" in datasource:
        source_name = format_looker_table_ref(
            getattr(datasource, "looker_explore_reference")
        )
    else:
        source_name = format_bq_table_ref(
            getattr(datasource, "bigquery_table_reference")
        )

    print(source_name)
    display_schema(datasource.schema)


def handle_schema_response(resp):
    if "query" in resp:
        print(resp.query.question)
    elif "result" in resp:
        display_section_title("Schema resolved")
        print("Data sources:")
        for datasource in resp.result.datasources:
            display_datasource(datasource)


def handle_data_response(resp):
    if "query" in resp:
        query = resp.query
        display_section_title("Retrieval query")
        print(f"Query name: {query.name}")
        print(f"Question: {query.question}")
        print("Data sources:")
        for datasource in query.datasources:
            display_datasource(datasource)
    elif "generated_sql" in resp:
        display_section_title("SQL generated")
        print(resp.generated_sql)
    elif "result" in resp:
        display_section_title("Data retrieved")

        fields = [field.name for field in resp.result.schema.fields]
        d = {}
        for el in resp.result.data:
            for field in fields:
                if field in d:
                    d[field].append(el[field])
                else:
                    d[field] = [el[field]]

        display(pd.DataFrame(d))


def handle_chart_response(resp):
    def _value_to_dict(v):
        if isinstance(v, proto.marshal.collections.maps.MapComposite):
            return _map_to_dict(v)
        elif isinstance(v, proto.marshal.collections.RepeatedComposite):
            return [_value_to_dict(el) for el in v]
        elif isinstance(v, (int, float, str, bool)):
            return v
        else:
            return MessageToDict(v)

    def _map_to_dict(d):
        out = {}
        for k in d:
            if isinstance(d[k], proto.marshal.collections.maps.MapComposite):
                out[k] = _map_to_dict(d[k])
            else:
                out[k] = _value_to_dict(d[k])
        return out

    if "query" in resp:
        print(resp.query.instructions)
    elif "result" in resp:
        vegaConfig = resp.result.vega_config
        vegaConfig_dict = _map_to_dict(vegaConfig)
        alt.Chart.from_json(json_lib.dumps(vegaConfig_dict)).display()


def show_message(msg):
    m = msg.system_message
    if "text" in m:
        handle_text_response(getattr(m, "text"))
    elif "schema" in m:
        handle_schema_response(getattr(m, "schema"))
    elif "data" in m:
        handle_data_response(getattr(m, "data"))
    elif "chart" in m:
        handle_chart_response(getattr(m, "chart"))
    print("\n")