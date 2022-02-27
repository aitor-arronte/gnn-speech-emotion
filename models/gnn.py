from torch import nn
from torch_geometric.nn import GCNConv, GINConv, GCN2Conv
from torch.functional import F
from torch.nn import Linear


#GCNN baseline
class GCNN(nn.Module):

	def __init__(self):
		super().__init__()
		self.gconv1 = GCNConv(128, 64)
		self.gconv2 = GCNConv(64, 64)
		self.relu = nn.LeakyReLU()
		self.fc = Linear(64, 4)


	def forward(self, graph):
		x = self.gconv1(graph.x, graph.edge_index)
		x = self.relu(x)
		x = F.dropout(x, training=self.training)
		x = self.gconv2(x, graph.edge_index)
		x = F.dropout(x, training=self.training)
		out = self.fc(x)
		return out







