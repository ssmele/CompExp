import torch
import numpy as np
from torch.utils.tensorboard.writer import SummaryWriter

exp_writer = SummaryWriter('./runs')
for epoch in range(20):
    print(epoch)
    exp_writer.add_scalar('test/val', np.random.randint(0, 10), epoch)
    exp_writer.add_scalar('test/auc', np.random.randint(0, 10), epoch)
    exp_writer.add_scalar('train/val', np.random.randint(0, 10), epoch)
    exp_writer.add_scalar('test/f1', np.random.randint(0, 10), epoch)
    exp_writer.add_scalar('test/per', np.random.randint(0, 10), epoch)
exp_writer.close()