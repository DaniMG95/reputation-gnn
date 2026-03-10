import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
from brain.models.interfaces import ModelBotDetectorInterface


class BotDetectorGCN(ModelBotDetectorInterface):
    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int):
        super(BotDetectorGCN, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, data: Data):
        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index)

        return F.log_softmax(x, dim=1)