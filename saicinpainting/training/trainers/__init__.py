import logging
import torch
from saicinpainting.training.trainers.default import DefaultInpaintingTrainingModule


def get_training_model_class(kind):
    if kind == 'default':
        return DefaultInpaintingTrainingModule

    raise ValueError(f'Unknown trainer module {kind}')


def make_training_model(config):
    kind = config.training_model.kind
    kwargs = dict(config.training_model)
    kwargs.pop('kind')
    kwargs['use_ddp'] = config.trainer.kwargs.get('accelerator', None) == 'ddp'

    logging.info(f'Make training model {kind}')

    cls = get_training_model_class(kind)
    return cls(config, **kwargs)


def load_checkpoint(train_config, path, map_location='cuda', strict=True):
    model: torch.nn.Module = make_training_model(train_config)
    state = torch.load(path, map_location=map_location)

    if train_config.training_model.predict_only:
        keys_to_remove = keys_to_remove = [key for key in state["state_dict"].keys() if "val_evaluator" in key or "test_evaluator" in key]
        for key in keys_to_remove:
            del  state["state_dict"][key]

    model.load_state_dict(state['state_dict'], strict=strict)
    model.on_load_checkpoint(state)
    return model
