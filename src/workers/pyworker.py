# #!/usr/bin/env python

"""
This is the python worker.

It is made mostly for reference purposes.
Although it can be used for sandboxing or for calling a different python interpreter than the main one.
"""

import json
import sys


class PyWorker:
    def __init__(self):
        self._env = {}

    def run(self):
        while line := sys.stdin.readline():
            try:
                msg = json.loads(line)
            except json.JSONDecodeError as err:
                response = {"status": "error", "message": str(err)}
            else:
                match msg["cmd"]:
                    case "eval":
                        response = self.handle_eval(msg)
                    case "exec":
                        response = self.handle_exec(msg)
                    case "get":
                        response = self.handle_get(msg)
                    # case "assign":
                    #     response = self.handle_assign(msg),
                    case "call":
                        response = self.handle_call(msg)
                    case "delete":
                        response = self.handle_delete(msg)
                    case "export_arrow":
                        response = self.handle_export_arrow(msg)
                    case unknown_cmd:
                        raise ValueError(f"Unknown command: {unknown_cmd}")

            # print(f"{response=}")
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

    def store(self, value):
        self._env['_' + hex(id(value))] = value
        return id(value)

    def get(self, id):
        return self._env['_' + hex(id)]

    def delete(self, id):
        del self._env['_' + hex(id)]

    def handle_eval(self, msg):
        """Evaluate expression and store."""
        id = self.store(eval(msg["code"], self._env))
        return {"status": "ok", "id": id}

    def handle_exec(self, msg):
        """Execute code but don't store result."""
        exec(msg["code"], self._env)
        return {"status": "ok"}

    def handle_get(self, msg):
        """Retrieve a stored value."""
        value = self.get(msg["id"])
        return {"status": "ok", "value": value}

    def handle_call(self, msg):
        f = self._env[msg['function']]
        args = [self.get(arg["ref"]) for arg in msg['args']]
        id = self.store(f(*args))
        return {"status": "ok", "id": id}

    def handle_delete(self, msg):
        self.delete(msg["id"])
        return {"status": "ok"}

    def handle_export_arrow(self, msg):
        pass

if __name__ == '__main__':
    worker = PyWorker()
    worker.run()


    # if (length(line) == 0) {
    #   # Sys.sleep(0.01)
    #   next
    # }
#
# result
#
# }, error = function(e) {
#     list(status = "error", message = as.character(e$message))
# })
#
# writeLines(toJSON(response, auto_unbox = TRUE), con_out)
# flush(con_out)
# }
#


# suppressMessages({
#     library(jsonlite)
# library(uuid)
# })
#
# # ----------------------------
# # Remote object storage
# # ----------------------------
#
# # emptyenv()	niets
# # baseenv()	base R functies
# # globalenv()	alles wat user geladen heeft
# # .remote_env <- new.env(parent = emptyenv())
# # .remote_env <- new.env(parent = emptyenv())
# .remote_env <- new.env(parent = globalenv())
#
# generate_id <- function() {
#     paste0(".", UUIDgenerate())
# }
#
# store_object <- function(value) {
#     id <- generate_id()
# assign(id, value, envir = .remote_env)
# return(id)
# }
#
# get_object <- function(id) {
# if (!exists(id, envir = .remote_env, inherits = FALSE)) {
# stop(paste("Object not found:", id))
# }
# get(id, envir = .remote_env, inherits = FALSE)
# }
#
# delete_object <- function(id) {
# if (exists(id, envir = .remote_env, inherits = FALSE)) {
# rm(list = id, envir = .remote_env)
# }
# TRUE
# }
#
# # ----------------------------
# # Command handlers
# # ----------------------------
#
# handle_eval <- function(msg) {
# value <- eval(parse(text = msg$code), envir = .remote_env)
# id <- store_object(value)
# list(status = "ok", id = id)
# }
#
# handle_get <- function(msg) {
# value <- get_object(msg$id)
# list(status = "ok", value = value)
# }
#
# handle_assign <- function(msg) {
# value <- get_object(msg$id)
# assign(msg$name, value, envir = .remote_env)
# list(status = "ok")
# }
#
# handle_call <- function(msg) {
# fn <- match.fun(msg$`function`)
#
# args <- lapply(msg$args, function(arg) {
# if (is.list(arg) && !is.null(arg$ref)) {
#     get_object(arg$ref)
# } else {
#     arg
# }
# })
#
# result <- do.call(fn, args)
# id <- store_object(result)
#
# list(status = "ok", id = id)
# }
#
# handle_delete <- function(msg) {
# delete_object(msg$id)
# list(status = "ok")
# }
#
# # For big dataframes
# handle_export_arrow <- function(msg) {
# library(arrow)
#
# df <- get_object(msg$id)
#
# path <- tempfile(fileext = ".arrow")
# write_ipc_stream(df, path)
#
# list(status="ok", path=path)
# }
#
# # ----------------------------
# # Main loop
# # ----------------------------
#
# con_in <- file("stdin", open = "r")
# con_out <- stdout()
#
# while (TRUE) {
# # print('start reading')
# line <- readLines(con_in, n = 1, warn = FALSE)
# # print(line)
#
# # if (length(line) == 0) {
# #   # Sys.sleep(0.01)
# #   next
# # }
# if (length(line) == 0) break;
#
# response <- tryCatch({
#     msg <- fromJSON(line, simplifyVector = FALSE)
#
# result <- switch(
#     msg$cmd,
# eval   = handle_eval(msg),
# get    = handle_get(msg),
# assign = handle_assign(msg),
# call   = handle_call(msg),
# delete = handle_delete(msg),
# export_arrow = handle_export_arrow(msg),
# stop(paste("Unknown command:", msg$cmd))
# )
#
# result
#
# }, error = function(e) {
#     list(status = "error", message = as.character(e$message))
# })
#
# writeLines(toJSON(response, auto_unbox = TRUE), con_out)
# flush(con_out)
# }
#