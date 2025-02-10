from impc_api import solr_request, batch_solr_request

# Execute the query
params={
'q': 'gene_symbol:Ucp1 AND significant:True',
'fl': 'gene_accession_id,parameter_name,id,weight,metadata'
}
#num_found, df = batch_solr_request(core='experiment', params=params, download=True, batch_size=100)

to_find="Carbon dioxide production"
#to_find="Total food intake"

params={
'q': f'marker_symbol:Ucp1 AND procedure_name:"Indirect Calorimetry" AND parameter_name:"{to_find}" AND significant:False',
'fl': 'procedure_name,colony_id,parameter_name,metadata_group,id,doc_id,zygosity,parameter_stable_id,strain_name,production_center,pipeline_stable_id'
}
batch_solr_request(core='statistical-result', params=params, download=True, batch_size=100)


# Note: the fields here are the fields from the sheets we can download for food intake, carbon dioxide, etc.
# First we find colony id above, from the statistical result panel, this is then used to find associated experiments
params={
#'q': f'colony_id:HMGU-HEPD0676_4_E07-1-1 AND parameter_name:"{to_find}"',
#'q': f'parameter_name:"{to_find}" AND metadata_group:593a2d0df1def577e4a39c6de7075687 AND zygosity: "homozygote" AND -gene_symbol:* AND parameter_stable_id:IMPC_CAL_004_001 AND strain_name:"C57BL/6NTac" AND biological_sample_group: "control"', # for control of specific gene
'q': f'parameter_name:"{to_find}" AND metadata_group:593a2d0df1def577e4a39c6de7075687 AND zygosity: "homozygote" AND gene_symbol:Ucp1 AND parameter_stable_id:IMPC_CAL_004_001 AND strain_name:"C57BL/6NTac" AND biological_sample_group: "experimental"', # for knockout of specific gene
#'q': f'metadata_group:593a2d0df1def577e4a39c6de7075687 AND parameter_name:"{to_find}" AND procedure_name:"Indirect Calorimetry"',
'fl': 'weight,file_type,data_point,external_sample_id,time_point,window_weight,discrete_point,strain_name,metadata_group,parameter_stable_id,gene_symbol',
'rows': 15000,
'wt': 'csv'
}

#num_found, df = batch_solr_request(core='experiment', params=params, download=True, batch_size=200)
#num_res, res = solr_request(core='experiment', params=params)
batch_solr_request(core='experiment', params=params, download=True, batch_size=100, filename='UCP1_knockouts')

params={
#'q': f'colony_id:HMGU-HEPD0676_4_E07-1-1 AND parameter_name:"{to_find}"',
'q': f'parameter_name:"{to_find}" AND metadata_group:593a2d0df1def577e4a39c6de7075687 AND zygosity: "homozygote" AND -gene_symbol:* AND parameter_stable_id:IMPC_CAL_004_001 AND strain_name:"C57BL/6NTac" AND biological_sample_group: "control"', # for control of specific gene
#'q': f'parameter_name:"{to_find}" AND metadata_group:593a2d0df1def577e4a39c6de7075687 AND zygosity: "homozygote" AND gene_symbol:Ucp1 AND parameter_stable_id:IMPC_CAL_004_001 AND strain_name:"C57BL/6NTac" AND biological_sample_group: "experimental"', # for knockout of specific gene
#'q': f'metadata_group:593a2d0df1def577e4a39c6de7075687 AND parameter_name:"{to_find}" AND procedure_name:"Indirect Calorimetry"',
'fl': 'weight,file_type,data_point,external_sample_id,time_point,window_weight,discrete_point,strain_name,metadata_group,parameter_stable_id,gene_symbol',
'rows': 15000,
'wt': 'csv'
}


batch_solr_request(core='experiment', params=params, download=True, batch_size=10000, filename='UCP1_controls')

#print("results:")
#print(res)


#print(num_found)
#print("the df:")
#print(df["weight"])
