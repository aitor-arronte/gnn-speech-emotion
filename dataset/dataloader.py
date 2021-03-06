import torch
import os
import torchaudio
from torch_geometric.utils import k_hop_subgraph, subgraph
import numpy as np

#Load graphs and audio samples
def data_loader(data_path):
		subs = os.listdir(data_path)
		graphs=[]
		max_len=[]
		for sub in subs:
			if os.path.isdir(data_path + sub+'/'):
				subdir = os.listdir(data_path + sub+'/')
				for sd in subdir:
					if os.path.isdir(data_path + sub+'/'+sd+'/'):
						files = os.listdir(data_path + sub+'/'+sd+'/')
						for f in files:
							if f.endswith('.pt'):
								g=torch.load(data_path + sub + '/' + sd + '/' + f)
								if g.num_nodes>5:
									graphs.append(g)
								else:
									continue
							elif f.endswith('.wav'):
								max_len.append(torchaudio.load(data_path + sub + '/' + sd + '/' + f)[0].shape[1])
		return graphs, max(max_len)


def audio_loader(audio_path):
	emo = {'ang': 0, 'hap': 1, 'neu': 2, 'sad': 3}
	subs = os.listdir(audio_path)
	samples = []
	max_len = []
	labels=[]
	for sub in subs:
		if os.path.isdir(audio_path + sub + '/'):
			subdir = os.listdir(audio_path + sub + '/')
			files = [f for f in subdir]
			for f in files:
				if f.endswith('.wav'):
					labels.append(emo[sub])
					samples.append(torchaudio.load(audio_path + sub +  '/' + f)[0])
					max_len.append(torchaudio.load(audio_path + sub + '/' + f)[0].shape[1])
	return samples, torch.tensor(labels), max(max_len)


#Create dataloader of graphs
def graph_loader(dir):
	subs = os.listdir(dir)
	graphs = []
	for sub in subs:
		if os.path.isdir(dir + sub + '/'):
			subdir = os.listdir(dir + sub + '/')
			for f in subdir:
				if f.endswith('.pt'):
					graph = torch.load(dir + sub + '/'+f)
					if graph.num_nodes >= 5:
						graphs.append(graph)
	return graphs


def save_tensors(audio_path, audio_path2, max_len):
	subs = os.listdir(audio_path)
	for sub in subs:
		if os.path.isdir(audio_path + sub + '/'):
			subdir = os.listdir(audio_path + sub + '/')
			files = [f for f in subdir]
			for f in files:
				if f.endswith('.wav'):
					t= torchaudio.load(audio_path + sub +  '/' + f)[0]
					t = padding_tensor(t, max_len)
					torch.save(t, audio_path2 + sub +  '/' + f.replace('.wav', '.pt'))


def tensor_loader(audio_path):
	emo = {'ang': 0, 'hap': 1, 'neu': 2, 'sad': 3}
	subs = os.listdir(audio_path)
	samples = []
	labels=[]
	for sub in subs:
		if os.path.isdir(audio_path + sub + '/'):
			subdir = os.listdir(audio_path + sub + '/')
			files = [f for f in subdir]
			for f in files:
				if f.endswith('.pt'):
					labels.append(emo[sub])
					samples.append(torch.load(audio_path + sub +  '/' + f))
	return samples, torch.tensor(labels)


def sample_subgraphs(graph, node_ids):
	subgraphs=[]
	for id in node_ids:
		sub=graph[id]
		subgraphs.append(sub)
	return subgraphs


def padding_tensor(sequences, max_len):
	"""
	input=list of tensors
	"""
	num = len(sequences)
	out_dims = (num, max_len)
	out_tensor = sequences[0].data.new(*out_dims).fill_(0)
	for i, tensor in enumerate(sequences):
		length = tensor.size(1)
		out_tensor[i, :length] = tensor
	return out_tensor


def get_subgraph(graph_data, hop=None, type='sub', batch_size=None):
	node_ids= list(np.random.choice(list(range(graph_data.num_nodes)), batch_size, replace=False))
	if type == 'sub':
		sg = subgraph(node_ids, graph_data.edge_index, graph_data.weight)
		return sg, sg[0].unique()
	elif hop is not None:
		sg = k_hop_subgraph(node_ids, hop, graph_data.edge_index)
		return sg


def write_file(file, list):
    file_out = open(file, 'w')
    for l in list:
        file_out.write(str(l)+"\n")
    file_out.close()
