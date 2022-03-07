import torch
import argparse
from train import train
import torchaudio
from models.gnn import GCNN
from models.speech_representations import ResidualBLSTM, Resblock
from pretrain import pretrain


def exec(graph_path, speech_model_path, batch_size=64, num_epochs=40):
	device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
	graph = torch.load(graph_path)
	speech_model = torch.load(speech_model_path)
	graph.x = get_speech_representations(speech_model, graph.node_id)
	model = GCNN()
	model.to(device)
	max_len = max([torchaudio.load(g)[0].shape[1] for g in graph.node_id ])
	train(model, device, max_len, num_epochs, batch_size, graph)


def get_speech_representations(speech_model, data):
	embeddings=[]
	for audio in data:
		x=speech_model(audio)
		embeddings.append(x)
	out = torch.tensor(embeddings)
	return out


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-ptrain', '--audio_path1', type=str, default='iemocap/train/',
	                    help='Pretrain the model. Provide IEMOCAP training data path.')

	parser.add_argument('-ptest', '--audio_path2', type=str, default='iemocap/test/',
	                    help='Pretrain the model. Provide IEMOCAP test data path.')

	parser.add_argument('-d', '--data_path', type=str, default = 'patterns/',
                        help='Data path to graph file.')

	parser.add_argument('-m', '--speech_model', type=str, default='pretrained/',
	                    help='path to the directory where the pretrained acoustic model is located.')

	parser.add_argument('-b', '--batch_size', type=int, default= 32,
	                    help='Batch size')

	parser.add_argument('-e', '--num_epochs', type=int, default=40,
	                    help='Number of epochs')

	args = parser.parse_args()

	if args.audio_path1 and args.audio_path2:
		device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		model = ResidualBLSTM(Resblock, [2])
		pretrain(model, device, args.num_epochs, args.batch_size, args.audio_path1, args.audio_path2)
	elif args.data_path:
		exec(args.data_path, args.speech_model, args.batch_size, args.num_epochs)
	else:
		print("please provide valid arguments. See -h for help.")